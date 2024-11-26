from dotenv import load_dotenv
import os
load_dotenv()

from app import create_app, db
from models import PromptTemplate

app = create_app()
with app.app_context():
    prompts = PromptTemplate.query.all()
    print('\nCurrent Prompt Templates:\n')
    for p in prompts:
        print(f'ID: {p.id}')
        print(f'Name: {p.name}')
        print(f'Type: {p.type}')
        print('Content:')
        print(p.template_content)
        print('---\n')
