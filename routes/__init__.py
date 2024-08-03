from flask import Blueprint

main_bp = Blueprint('main', __name__)
assistant_bp = Blueprint('assistant', __name__)
messages_bp = Blueprint('messages', __name__)

from .main import *
from .assistant import *
from .messages import *
