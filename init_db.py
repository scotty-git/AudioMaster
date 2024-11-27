from app import create_app, db
from models import *  # Import all models
from flask_migrate import Migrate, init, migrate, upgrade

def initialize_database():
    app = create_app()
    migrate = Migrate(app, db)
    
    with app.app_context():
        # Initialize migrations
        try:
            init()
            print("Initialized migrations directory")
        except Exception as e:
            print(f"Migrations directory might already exist: {e}")
        
        # Create initial migration
        migrate(message="Initial migration")
        print("Created initial migration")
        
        # Apply migrations
        upgrade()
        print("Applied migrations successfully")

if __name__ == '__main__':
    initialize_database()
