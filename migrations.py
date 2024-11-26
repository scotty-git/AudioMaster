from app import create_app, db
from flask_migrate import Migrate, upgrade
from flask.cli import FlaskGroup

app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(app)

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
