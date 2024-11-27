from app import create_app
from flask_sqlalchemy import SQLAlchemy

app = create_app()
db = SQLAlchemy(app)

with app.app_context():
    tables = list(db.engine.table_names())
    print("Database Tables:", tables)
