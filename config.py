import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chat.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_SESSION_KEY = os.getenv("OPENAI_SESSION_KEY")
    OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")
    AUTHENTICATION = os.getenv("AUTHENTICATION", False)
