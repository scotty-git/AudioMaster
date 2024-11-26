from dotenv import load_dotenv
import os
load_dotenv()

from app import create_app, db
from models import Template

template_data = {
    "title": "Personalised Self-Help Onboarding",
    "description": "A comprehensive questionnaire to gather information for creating personalized self-help audiobooks",
    "sections": [
        {
            "title": "About You",
            "questions": [
                {
                    "text": "What is your name?",
                    "type": "text"
                },
                {
                    "text": "How old are you?",
                    "type": "number"
                },
                {
                    "text": "What is your sex?",
                    "type": "text"
                },
                {
                    "text": "What is your occupation?",
                    "type": "text"
                },
                {
                    "text": "What is your current living situation? (e.g., single, married, living with partner, have children)",
                    "type": "text"
                }
            ]
        },
        {
            "title": "Your Strengths",
            "questions": [
                {
                    "text": "What do you, or ones close to you, consider to be your top 3 strengths? Try to give examples of them in action as well.",
                    "type": "textarea"
                }
            ]
        },
        {
            "title": "Personal Growth Journey",
            "questions": [
                {
                    "text": "Topic 1 - Please describe your first area of growth, including: current challenge, importance, goals, emotional impact, personal example, vision of success, and previous attempts",
                    "type": "textarea"
                },
                {
                    "text": "Topic 2 - Please describe your second area of growth, including all aspects mentioned above",
                    "type": "textarea"
                },
                {
                    "text": "Topic 3 - Please describe your third area of growth, including all aspects mentioned above",
                    "type": "textarea"
                },
                {
                    "text": "Topic 4 - Please describe your fourth area of growth, including all aspects mentioned above",
                    "type": "textarea"
                },
                {
                    "text": "Topic 5 (optional) - Please describe your fifth area of growth, including all aspects mentioned above",
                    "type": "textarea"
                },
                {
                    "text": "Topic 6 (optional) - Please describe your sixth area of growth, including all aspects mentioned above",
                    "type": "textarea"
                },
                {
                    "text": "Do you wish for each section to have similar weighting/length in the book, or would you like specific topics to have more focus? Please indicate preferred weightings.",
                    "type": "textarea"
                },
                {
                    "text": "Do you have a preference for the order in which these topics are addressed in the audiobook, or are you happy for the AI to determine the best flow?",
                    "type": "textarea"
                }
            ]
        },
        {
            "title": "Daily Life and Routines",
            "questions": [
                {
                    "text": "Please describe your current daily routine.",
                    "type": "textarea"
                },
                {
                    "text": "What would your ideal daily routine look like?",
                    "type": "textarea"
                },
                {
                    "text": "Are there any specific habits you're trying to build or break that you haven't mentioned earlier?",
                    "type": "textarea"
                }
            ]
        },
        {
            "title": "Learning Style and Preferences",
            "questions": [
                {
                    "text": "Are there any specific techniques, theories, approaches, self-help books, authors, or experts whose work has particularly resonated with you in the past? Please share why you found them helpful or interesting.",
                    "type": "textarea"
                },
                {
                    "text": "What type of voice and tone do you prefer for your audiobook? (e.g., 'Male voice with a calm, soothing tone', 'Female voice with an energetic, motivational style', etc.)",
                    "type": "textarea"
                }
            ]
        },
        {
            "title": "Final Thoughts",
            "questions": [
                {
                    "text": "Is there anything else you'd like to share that would help us create a truly personalized and impactful audiobook for you?",
                    "type": "textarea"
                }
            ]
        }
    ]
}

app = create_app()
with app.app_context():
    # Create the template
    template = Template(
        title=template_data['title'],
        description=template_data['description'],
        sections=template_data['sections']
    )
    
    # Add and commit to database
    db.session.add(template)
    db.session.commit()
    
    print(f"Template created successfully with ID: {template.id}")
