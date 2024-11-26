import openai
from flask import current_app
import json

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=current_app.config['OPENAI_API_KEY']
        )
    
    def generate_outline(self, questionnaire_responses):
        try:
            prompt = self._create_outline_prompt(questionnaire_responses)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert book outline creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            current_app.logger.error(f"AI Outline Generation Error: {str(e)}")
            raise
    
    def generate_chapter_content(self, outline_chapter):
        try:
            prompt = self._create_chapter_prompt(outline_chapter)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert book writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            current_app.logger.error(f"AI Chapter Generation Error: {str(e)}")
            raise
    
    def _create_outline_prompt(self, responses):
        return f"""Based on the following questionnaire responses, create a detailed book outline:
        
        {json.dumps(responses, indent=2)}
        
        Create a JSON response with the following structure:
        {{
            "title": "Book Title",
            "chapters": [
                {{
                    "number": 1,
                    "title": "Chapter Title",
                    "summary": "Brief chapter summary",
                    "key_points": ["point 1", "point 2"]
                }}
            ]
        }}
        """
    
    def _create_chapter_prompt(self, chapter):
        return f"""Write a detailed chapter based on the following outline:
        
        Title: {chapter['title']}
        Summary: {chapter['summary']}
        Key Points: {', '.join(chapter['key_points'])}
        
        Write a comprehensive chapter that covers all key points while maintaining
        an engaging narrative flow.
        """
