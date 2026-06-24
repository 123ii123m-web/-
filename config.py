import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    OWNER_ID = 6300997264  # ایدی عددی خودت

    # AI APIs
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER")
    GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")

    # Storage group
    GROUP_ID = -1004397313215

    # AI model names
    OPENAI_MODEL = "gpt-4o"
    DEEPSEEK_MODEL = "deepseek-chat"
    GROQ_MODEL = "llama-3.3-70b-versatile"

    @classmethod
    def validate(cls):
        required = ["TELEGRAM_BOT_TOKEN"]
        missing = [r for r in required if not getattr(cls, r)]
        if missing:
            raise ValueError(f"Missing: {', '.join(missing)}")
        if not cls.GROUP_ID:
            raise ValueError("GROUP_ID is required")
