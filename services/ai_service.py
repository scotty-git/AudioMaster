import openai
from flask import current_app
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from openai import OpenAIError, APIError, RateLimitError

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        self.max_retries = 2
        self.base_wait = 1
        self.request_timeout = 60
        self._verify_api_key()

    def _verify_api_key(self):
        """Verify that the OpenAI API key is valid and working."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Verify API connection"},
                    {"role": "user", "content": "Test"}
                ],
                max_tokens=5
            )
            current_app.logger.info("OpenAI API key verification successful")
        except OpenAIError as e:
            current_app.logger.error(f"OpenAI API error: {str(e)}")
            raise ValueError("OpenAI API error. Please check your configuration.")
            
    @retry(stop=stop_after_attempt(2), 
           wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=lambda e: isinstance(e, (RateLimitError, APIError)))
    def generate_outline(self, questionnaire_responses):
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            start_time = time.time()
            try:
                prompt = self._create_outline_prompt(questionnaire_responses)
                current_app.logger.info(f"Generating outline with OpenAI (attempt {retry_count + 1}/{max_retries})")
                
                # Check for timeout
                if time.time() - start_time > self.request_timeout:
                    raise TimeoutError("Request timeout: Generation taking too long")

                response = self.client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {"role": "system", "content": """You are an expert book outline creator specializing in creating well-structured, engaging book outlines. 
                         CRITICAL: You must respond with ONLY valid JSON. No additional text, comments, or explanations.
                         Focus on maintaining narrative flow and ensuring each chapter builds upon previous ones.
                         Your response will be parsed as JSON, any deviation from JSON format will cause an error."""},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    presence_penalty=0.3,
                    frequency_penalty=0.3,
                    response_format={"type": "json_object"},  # Enforce JSON response format
                    timeout=self.request_timeout
                )
                
                content = response.choices[0].message.content
                outline = self._validate_outline_json(content)
                current_app.logger.info("Successfully generated and validated outline")
                return outline
                
            except json.JSONDecodeError as e:
                retry_count += 1
                current_app.logger.warning(f"Invalid JSON format (attempt {retry_count}/{max_retries}): {str(e)}")
                if retry_count >= max_retries:
                    raise ValueError("AI response validation failed: Invalid JSON format. Please try again.")
                continue
                
            except ValueError as e:
                retry_count += 1
                current_app.logger.warning(f"Validation error (attempt {retry_count}/{max_retries}): {str(e)}")
                if retry_count >= max_retries:
                    raise ValueError(f"AI response validation failed: {str(e)}")
                continue
                
            except RateLimitError as e:
                current_app.logger.warning(f"Rate limit hit: {str(e)}")
                raise ValueError("AI service is currently busy. Please wait a moment and try again.")
                
            except APIError as e:
                current_app.logger.error(f"OpenAI API Error: {str(e)}")
                raise ValueError("AI service encountered an error. Please try again.")
                
            except TimeoutError as e:
                current_app.logger.error(f"Timeout Error: {str(e)}")
                raise ValueError("Request timed out. The outline generation is taking longer than expected. Please try again.")
                
            except Exception as e:
                current_app.logger.error(f"AI Outline Generation Error: {str(e)}")
                raise ValueError("An unexpected error occurred. Please try again.")
    
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
    
    def _validate_outline_json(self, content):
        """Validate the outline JSON structure."""
        try:
            data = json.loads(content)
            required_fields = {'title', 'chapters'}
            chapter_fields = {'number', 'title', 'summary', 'key_points', 'estimated_duration'}
            
            if not all(field in data for field in required_fields):
                raise ValueError(f"Missing required fields. Must include: {required_fields}")
                
            if not isinstance(data['chapters'], list) or not data['chapters']:
                raise ValueError("Chapters must be a non-empty array")
                
            for chapter in data['chapters']:
                if not all(field in chapter for field in chapter_fields):
                    raise ValueError(f"Each chapter must include: {chapter_fields}")
                if not isinstance(chapter['key_points'], list):
                    raise ValueError("key_points must be an array")
                    
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
            
    def _create_outline_prompt(self, responses):
        return f"""You are a professional book outline creator. Generate a detailed book outline optimized for audio format based on these questionnaire responses:

{json.dumps(responses, indent=2)}

IMPORTANT: Respond ONLY with a valid JSON object. Do not include any explanatory text.

The JSON response MUST follow this exact structure:
{{
    "title": "Book Title",
    "chapters": [
        {{
            "number": 1,
            "title": "Chapter Title",
            "summary": "Brief yet detailed chapter summary (2-3 sentences)",
            "key_points": [
                "Key point 1 - specific and actionable",
                "Key point 2 - clear and concise",
                "Key point 3 - memorable takeaway"
            ],
            "estimated_duration": "15-20 minutes"
        }}
    ]
}}

Guidelines:
1. Create 5-7 well-structured chapters
2. Each chapter must be self-contained but connected
3. Ensure smooth transitions between topics
4. Keep audio format in mind - clear structure, memorable points
5. Each chapter should be 15-20 minutes when narrated

REQUIREMENTS:
- ALL fields shown in the structure are required
- 'number' must be an integer starting from 1
- 'key_points' must be an array with 3-5 points
- 'estimated_duration' should be in the format "X-Y minutes"
- Use proper JSON formatting with double quotes
- Numbers should not be quoted
- No comments or additional text allowed

Ensure each chapter is substantial enough for audio content but not too long for comfortable listening."""
    
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
