import openai
from flask import current_app
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import RateLimitError, APIError

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=current_app.config['OPENAI_API_KEY']
        )
        self.max_retries = 3
        self.base_wait = 1
    
    @retry(stop=stop_after_attempt(3), 
           wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=lambda e: isinstance(e, (RateLimitError, APIError)))
    def generate_outline(self, questionnaire_responses):
        try:
            prompt = self._create_outline_prompt(questionnaire_responses)
            current_app.logger.info("Generating outline with OpenAI")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert book outline creator specializing in creating well-structured, engaging book outlines. Focus on maintaining narrative flow and ensuring each chapter builds upon previous ones."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                presence_penalty=0.3,
                frequency_penalty=0.3
            )
            
            outline = json.loads(response.choices[0].message.content)
            current_app.logger.info("Successfully generated outline")
            return outline
            
        except RateLimitError as e:
            current_app.logger.warning(f"Rate limit hit: {str(e)}")
            raise
        except APIError as e:
            current_app.logger.error(f"OpenAI API Error: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            current_app.logger.error(f"Invalid JSON in response: {str(e)}")
            raise ValueError("Failed to parse AI response")
        except Exception as e:
            current_app.logger.error(f"AI Outline Generation Error: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), 
           wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=lambda e: isinstance(e, (RateLimitError, APIError)))
    def generate_chapter_content(self, outline_chapter):
        try:
            prompt = self._create_chapter_prompt(outline_chapter)
            current_app.logger.info(f"Generating content for chapter {outline_chapter.get('number', 'unknown')}")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert book writer with a talent for creating engaging, flowing narrative content that maintains consistency and readability while being suitable for audio format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                presence_penalty=0.3,
                frequency_penalty=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            current_app.logger.info(f"Successfully generated chapter {outline_chapter.get('number', 'unknown')} content")
            return content
            
        except RateLimitError as e:
            current_app.logger.warning(f"Rate limit hit during chapter generation: {str(e)}")
            raise
        except APIError as e:
            current_app.logger.error(f"OpenAI API Error during chapter generation: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"AI Chapter Generation Error: {str(e)}")
            raise
    
    def _create_outline_prompt(self, responses):
        return f"""Based on the following questionnaire responses, create a detailed book outline that is optimized for audio format and engaging listening experience:
        
        {json.dumps(responses, indent=2)}
        
        Please create a well-structured outline that:
        1. Maintains a clear narrative flow between chapters
        2. Ensures each chapter builds upon previous content
        3. Includes transition points between major topics
        4. Considers the audio listening experience
        
        Create a JSON response with the following structure:
        {{
            "title": "Book Title",
            "chapters": [
                {{
                    "number": 1,
                    "title": "Chapter Title",
                    "summary": "Detailed chapter summary including main themes and flow",
                    "key_points": ["Specific key point 1", "Specific key point 2"],
                    "estimated_duration": "15-20 minutes"
                }}
            ]
        }}
        
        Ensure each chapter is substantial enough for audio content but not too long for comfortable listening.
        """
    
    def _create_chapter_prompt(self, chapter):
        return f"""Write a detailed chapter optimized for audio narration based on the following outline:
        
        Title: {chapter['title']}
        Summary: {chapter['summary']}
        Key Points: {', '.join(chapter['key_points'])}
        
        Please follow these guidelines:
        1. Write in a clear, conversational style suitable for audio narration
        2. Use natural transitions between topics
        3. Include engaging examples and illustrations of concepts
        4. Avoid complex technical jargon unless necessary
        5. Use clear paragraph breaks and section transitions
        6. Maintain consistent pacing and flow
        7. Include verbal signposts for audio listeners
        
        Write a comprehensive chapter that:
        - Introduces the topic clearly
        - Develops each key point with sufficient detail
        - Provides smooth transitions between sections
        - Concludes with a clear summary
        - Uses language optimized for audio consumption
        """
