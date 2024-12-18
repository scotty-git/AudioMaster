from app import db
from datetime import datetime
import uuid
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Template(db.Model):
    __tablename__ = 'templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    sections = db.Column(db.JSON, nullable=False)
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    questionnaire_responses = db.relationship('QuestionnaireResponse', backref='template', lazy=True)

class QuestionnaireResponse(db.Model):
    __tablename__ = 'questionnaire_responses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('templates.id'), nullable=False)
    responses = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default='submitted')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    book_outline = db.relationship('BookOutline', backref='questionnaire', lazy=True, uselist=False)

class BookOutline(db.Model):
    __tablename__ = 'book_outlines'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    questionnaire_id = db.Column(db.String(36), db.ForeignKey('questionnaire_responses.id'), nullable=False)
    chapters = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    audiobook = db.relationship('Audiobook', backref='outline', lazy=True, uselist=False)

class Audiobook(db.Model):
    __tablename__ = 'audiobooks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    outline_id = db.Column(db.String(36), db.ForeignKey('book_outlines.id'), nullable=False)
    chapter_files = db.Column(db.JSON, nullable=False)
    total_duration = db.Column(db.Integer)
    status = db.Column(db.String(20), default='generating')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PromptTemplate(db.Model):
    __tablename__ = 'prompt_templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20), nullable=False)  # 'outline' or 'chapter'
    template_content = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON)  # Store variable definitions
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)