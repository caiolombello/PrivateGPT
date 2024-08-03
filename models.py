from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

class Thread(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String, unique=True, nullable=False)
    assistant_id = db.Column(db.String, nullable=False)
    chat_name = db.Column(db.String, nullable=False, default="New chat")

class Message(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    thread_id = db.Column(db.String, db.ForeignKey('thread.name'), nullable=False)
    role = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)

class Assistant(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    assistant_id = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    tool_enabled = db.Column(db.Boolean, default=False, nullable=False)