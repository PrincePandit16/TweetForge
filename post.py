import os
from dotenv import load_dotenv
load_dotenv()  # Loads all keys from .env before anything else

import tweepy
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
import operator
from pydantic import BaseModel, Field


generator_llm  = ChatGroq(model="llama-3.3-70b-versatile")
evaluator_llm  = ChatGroq(model="llama-3.3-70b-versatile")
optimizer_llm  = ChatGroq(model="openai/gpt-oss-120b")


x_client = tweepy.Client(
    bearer_token=os.getenv("X_BEARER_TOKEN"),
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
)


class TweetEvaluation(BaseModel):
    evaluation: Literal["approved", "needs_improvement"] = Field(..., description="Final evaluation result.")
    feedback: str = Field(..., description="Feedback for the tweet.")

structured_evaluator_llm = evaluator_llm.with_structured_output(TweetEvaluation)


class TweetState(TypedDict):
    topic: str
    tweet: str
    evaluation: Literal["approved", "needs improvement"]
    feedback: str
    iteration: int
    max_iteration: int
    tweet_history: Annotated[list[str], operator.add]
    feedback_history: Annotated[list[str], operator.add]
    posted_tweet_id: str   # filled after posting


def generate_tweet(state: TweetState):
    messages = [
        SystemMessage(content="You are a funny and clever Twitter/X influencer."),
        HumanMessage(content=f"""
            Write a short, original, and hilarious tweet on the topic: "{state['topic']}".

            Rules:
            - Do NOT use question-answer format.
            - Max 280 characters.
            - Use observational humor, irony, sarcasm, or cultural references.
            - Think in meme logic, punchlines, or relatable takes.
            - Use simple, day-to-day English.
        """)
    ]
    response = generator_llm.invoke(messages).content
    return {"tweet": response}


def evaluate_tweet(state: TweetState):
    messages = [
        SystemMessage(content="You are a ruthless, no-laugh-given Twitter critic."),
        HumanMessage(content=f"""
            Evaluate the following tweet:

            Tweet: "{state['tweet']}"

            Criteria:
            1. Originality – Is this fresh?
            2. Humor – Did it genuinely make you laugh?
            3. Punchiness – Short, sharp, scroll-stopping?
            4. Virality Potential – Would people retweet it?
            5. Format – Well-formed tweet (not Q&A, under 280 chars)?

            Auto-reject if:
            - Question-answer format
            - Exceeds 280 characters
            - Traditional setup-punchline joke
            - Ends with a generic, throwaway line

            Respond in structured format:
            - evaluation: "approved" or "needs_improvement"
            - feedback: one paragraph on strengths and weaknesses
        """)
    ]
    response = structured_evaluator_llm.invoke(messages)
    return {
        "evaluation": response.evaluation,
        "feedback": response.feedback,
        "feedback_history": [response.feedback],
    }


def optimize_tweet(state: TweetState):
    messages = [
        SystemMessage(content="You punch up tweets for virality and humor based on given feedback."),
        HumanMessage(content=f"""
            Improve the tweet based on this feedback:
            "{state['feedback']}"

            Topic: "{state['topic']}"
            Original Tweet:
            {state['tweet']}

            Re-write it as a short, viral-worthy tweet. Avoid Q&A style and stay under 280 characters.
        """)
    ]
    response = optimizer_llm.invoke(messages).content
    iteration = state["iteration"] + 1
    return {"tweet": response, "iteration": iteration, "tweet_history": [response]}


def post_tweet(state: TweetState):
    """Post the approved tweet to X and save the tweet ID."""
    try:
        response = x_client.create_tweet(text=state["tweet"])
        tweet_id = response.data["id"]
        print(f"✅ Tweet posted! ID: {tweet_id}")
        print(f"   URL: https://twitter.com/i/web/status/{tweet_id}")
        return {"posted_tweet_id": tweet_id}
    except tweepy.TweepyException as e:
        print(f"❌ Failed to post tweet: {e}")
        return {"posted_tweet_id": ""}


def route_evaluation(state: TweetState):
    if state["evaluation"] == "approved" or state["iteration"] >= state["max_iteration"]:
        return "approved"
    return "needs_improvement"


graph = StateGraph(TweetState)

graph.add_node("generate", generate_tweet)
graph.add_node("evaluate", evaluate_tweet)
graph.add_node("optimize", optimize_tweet)
graph.add_node("post", post_tweet)          # ← new node

graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges(
    "evaluate",
    route_evaluation,
    {"approved": "post", "needs_improvement": "optimize"},  # approved → post
)
graph.add_edge("optimize", "evaluate")
graph.add_edge("post", END)

workflow = graph.compile()


if __name__ == "__main__":
    initial_state = {
        "topic": "getting a job now in india",
        "iteration": 1,
        "max_iteration": 1,
    }
    result = workflow.invoke(initial_state)

    print("\n── Final Tweet ──")
    print(result["tweet"])
    print(f"\nIterations: {result['iteration']}")
    print(f"Evaluation: {result['evaluation']}")