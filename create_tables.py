from dotenv import load_dotenv
import os
load_dotenv()

from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print("Tables created successfully!")
