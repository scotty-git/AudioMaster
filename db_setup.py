from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import shutil
from app import create_app, db

def setup_database():
    app = create_app()
    migrate = Migrate(app, db)
    
    with app.app_context():
        # Remove existing migrations if any
        if os.path.exists('migrations'):
            shutil.rmtree('migrations')
        
        # Create migrations directory
        os.makedirs('migrations/versions', exist_ok=True)
        
        # Initialize migrations
        os.system('flask db init')
        
        # Create initial migration
        os.system('flask db migrate -m "Initial migration"')
        
        # Apply migration
        os.system('flask db upgrade')
        
        print("Database setup completed successfully!")

if __name__ == '__main__':
    setup_database()
