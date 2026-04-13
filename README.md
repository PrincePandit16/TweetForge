# 🤖 AI Tweet Generator with LangGraph

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge&logo=groq&logoColor=white)
![Tweepy](https://img.shields.io/badge/Tweepy-v4%2B-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![dotenv](https://img.shields.io/badge/dotenv-secured-ECD53F?style=for-the-badge&logo=dotenv&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

An autonomous tweet generation pipeline built with **LangGraph** that generates, evaluates, and optimizes tweets using LLMs — then posts them to X (Twitter) via the API.

---

## 🧠 How It Works

```
START → Generate Tweet → Evaluate Tweet → [Approved?]
                                              ├── YES → Post to X → END
                                              └── NO  → Optimize Tweet → Evaluate Tweet (loop)
```

The pipeline runs a feedback loop between a **generator**, a **critic**, and an **optimizer** — iterating until the tweet is approved or hits the max iteration limit.

| Node | Model | Role |
|---|---|---|
| Generator | `llama-3.3-70b-versatile` | Writes the original tweet |
| Evaluator | `llama-3.3-70b-versatile` | Critiques for humor, virality, format |
| Optimizer | `openai/gpt-oss-120b` | Rewrites based on feedback |
| Poster | Tweepy v2 | Posts approved tweet to X |

---

## 📁 Project Structure

```
tweet-generator/
├── post.py          # Main pipeline script
├── .env             # API keys (never commit this)
├── .gitignore
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/tweet-generator.git
cd tweet-generator
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install langgraph langchain-groq langchain-core tweepy python-dotenv pydantic
```

### 4. Set up your `.env` file

Create a `.env` file in the root folder:

```env
# Groq
GROQ_API_KEY=your_groq_api_key_here

# X / Twitter API v2
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
X_BEARER_TOKEN=your_bearer_token_here
```

#### Where to get these keys:
- **Groq API key** → [console.groq.com](https://console.groq.com)
- **X API keys** → [developer.twitter.com](https://developer.twitter.com) → Your App → *Keys and Tokens*

> ⚠️ Make sure your X app has **Read and Write** permissions before generating access tokens.

---

## 🚀 Run

```bash
python post.py
```

### Expected output

```
✅ Tweet posted! ID: 1234567890123456789
   URL: https://twitter.com/i/web/status/1234567890123456789

── Final Tweet ──
Getting a job in India: where your resume gets more rejections than a Tinder profile.

Iterations: 2
Evaluation: approved
```

---

## 🛠️ Configuration

Edit the `initial_state` at the bottom of `post.py` to change the topic or iteration limit:

```python
initial_state = {
    "topic": "getting a job now in india",  # ← change topic here
    "iteration": 1,
    "max_iteration": 5,                     # ← max optimization loops
}
```

---

## 💾 Dry Run (No X API needed)

To test the pipeline without posting to X, swap the `post_tweet` function in `post.py`:

```python
def post_tweet(state: TweetState):
    import json
    from datetime import datetime

    entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": state["topic"],
        "tweet": state["tweet"],
        "iterations": state["iteration"],
    }

    with open("tweets_log.json", "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"💾 Tweet saved to tweets_log.json")
    return {"posted_tweet_id": "saved_locally"}
```

This saves all generated tweets locally — no API credits required.

---

## ❗ Troubleshooting

| Error | Fix |
|---|---|
| `401 Unauthorized` | Regenerate tokens **after** enabling Read+Write on your X app |
| `402 Payment Required` | X API requires credits — add billing at developer.twitter.com or use dry run mode |
| `403 Forbidden` | Your X app needs at least the Basic tier for posting |
| `GROQ_API_KEY not found` | Make sure `.env` is in the same directory as `post.py` |
| `ModuleNotFoundError` | Run `pip install <module>` inside your activated virtual environment |

---

## 🔧 Tech Stack

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=flat-square&logo=groq&logoColor=white)
![Tweepy](https://img.shields.io/badge/Tweepy-v4%2B-1DA1F2?style=flat-square&logo=twitter&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)
![dotenv](https://img.shields.io/badge/dotenv-secured-ECD53F?style=flat-square&logo=dotenv&logoColor=black)

- [LangGraph](https://github.com/langchain-ai/langgraph) — stateful agent pipeline
- [LangChain Groq](https://python.langchain.com/docs/integrations/chat/groq/) — LLM provider
- [Tweepy](https://www.tweepy.org/) — X (Twitter) API client
- [Pydantic](https://docs.pydantic.dev/) — structured LLM output validation
- [python-dotenv](https://pypi.org/project/python-dotenv/) — environment variable management

---

## 📄 License

MIT License — feel free to use and modify.
