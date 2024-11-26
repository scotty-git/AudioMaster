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
    type = db.Column(db.String(20), nullable=False)
    template_content = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)
    last_edited_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    editor = db.relationship('User', foreign_keys=[last_edited_by])
    versions = db.relationship('PromptTemplateVersion', backref='template', lazy='dynamic')
    
    def create_version(self, user_id):
        """Create a new version of this template"""
        version = PromptTemplateVersion(
            prompt_template_id=self.id,
            version=self.version,
            name=self.name,
            description=self.description,
            type=self.type,
            template_content=self.template_content,
            variables=self.variables,
            edited_by=user_id
        )
        db.session.add(version)
        self.version += 1
        self.last_edited_by = user_id
        return version

class PromptTemplateVersion(db.Model):
    __tablename__ = 'prompt_template_versions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_template_id = db.Column(db.String(36), db.ForeignKey('prompt_templates.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20), nullable=False)
    template_content = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON)
    edited_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    editor = db.relationship('User', foreign_keys=[edited_by])
    
    __table_args__ = (
        db.UniqueConstraint('prompt_template_id', 'version', name='uix_template_version'),
    )