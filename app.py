import os
from flask import Flask
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler

class Base(DeclarativeBase):
    pass

csrf = CSRFProtect()

db = SQLAlchemy(model_class=Base)
migrate = Migrate()
login = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')
    app.config['DEFAULT_USER_ID'] = '00000000-0000-0000-0000-000000000000'  # Default user ID for versioning
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    login.login_view = 'auth.login'
    
    # Setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/audiov4.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('AudioV4 startup')
    
    # Register blueprints
    from routes import templates, questionnaires, outlines, audiobooks, prompts, docs
    
    # Configure user loader
    from models import User
    
    @login.user_loader
    def load_user(id):
        return User.query.get(str(id))

    app.register_blueprint(templates.bp)
    app.register_blueprint(questionnaires.bp)
    app.register_blueprint(outlines.bp)
    app.register_blueprint(audiobooks.bp)
    app.register_blueprint(prompts.bp)
    app.register_blueprint(docs.docs)  # Register the docs blueprint
    
    # Add root route
    @app.route('/')
    def index():
        return redirect(url_for('templates.list_templates'))
    
    return app
