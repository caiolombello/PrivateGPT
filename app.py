from flask import Flask
from config import Config
from models import db
from routes import main_bp, assistant_bp, messages_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(main_bp)
app.register_blueprint(assistant_bp, url_prefix='/assistant')
app.register_blueprint(messages_bp, url_prefix='/messages')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    response.cache_control.proxy_revalidate = True
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
