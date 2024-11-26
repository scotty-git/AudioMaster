from dotenv import load_dotenv
import os
load_dotenv()

from app import create_app, db
from models import PromptTemplate

enhanced_prompt = '''Based on the following questionnaire responses, create a detailed book outline optimized for audio format and engaging listening experience:

{responses}

Please create a well-structured outline that follows these principles:

1. Narrative Flow:
   - Maintain a clear, logical progression between chapters
   - Ensure smooth transitions between topics
   - Build complexity gradually
   - Create emotional resonance through storytelling

2. Chapter Structure:
   - Begin with foundational concepts
   - Progress to more advanced applications
   - Include practical exercises and reflection points
   - End with actionable takeaways

3. Content Guidelines:
   - Focus on personal growth areas identified in the questionnaire
   - Incorporate the user's strengths into solutions
   - Reference preferred learning styles and approaches
   - Adapt to daily routines and habits
   - Use the preferred voice and tone specified

4. Audio Optimization:
   - Structure content for easy listening
   - Include verbal signposts and transitions
   - Keep chapters to digestible lengths (15-25 minutes)
   - Use clear, conversational language

Create a JSON response with the following structure:
{
    "title": "Book Title",
    "chapters": [
        {
            "number": 1,
            "title": "Chapter Title",
            "summary": "Detailed chapter summary including main themes and flow",
            "key_points": [
                "Key point 1 - Include specific, actionable items",
                "Key point 2 - Focus on practical implementation",
                "Key point 3 - Connect to personal examples"
            ],
            "estimated_duration": "15-20 minutes",
            "exercises": [
                "Practical exercise or reflection point 1",
                "Practical exercise or reflection point 2"
            ],
            "transitions": {
                "intro": "How this chapter opens and connects to previous content",
                "outro": "How this chapter concludes and leads to the next"
            }
        }
    ],
    "theme": {
        "voice_style": "Based on user preference",
        "tone": "Based on user preference",
        "pacing": "Balanced for audio consumption"
    }
}

Ensure the outline:
1. Respects the user's preferred topic weightings
2. Follows their preferred topic order (if specified)
3. Integrates their daily routine considerations
4. Incorporates their mentioned strengths
5. References their successful past experiences
6. Aligns with their preferred learning style'''

app = create_app()
with app.app_context():
    # Get the existing prompt
    prompt = PromptTemplate.query.filter_by(type='outline').first()
    
    if prompt:
        # Update the existing prompt
        prompt.template_content = enhanced_prompt
        prompt.description = "Enhanced template for generating personalized self-help book outlines"
        db.session.commit()
        print(f"Updated prompt template with ID: {prompt.id}")
    else:
        # Create a new prompt if none exists
        new_prompt = PromptTemplate(
            name="Enhanced Book Outline Generator",
            description="Enhanced template for generating personalized self-help book outlines",
            type="outline",
            template_content=enhanced_prompt,
            variables={"responses": "JSON object containing questionnaire responses"}
        )
        db.session.add(new_prompt)
        db.session.commit()
        print(f"Created new prompt template with ID: {new_prompt.id}")
