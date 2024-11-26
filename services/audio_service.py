from flask import current_app
import openai
import os
import uuid

class AudioService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=current_app.config['OPENAI_API_KEY']
        )
    
    def generate_audio(self, text, filename=None):
        try:
            if filename is None:
                filename = f"{uuid.uuid4()}.mp3"
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            # Ensure audio directory exists
            os.makedirs('static/audio', exist_ok=True)
            
            # Save the audio file
            audio_path = os.path.join('static/audio', filename)
            with open(audio_path, 'wb') as f:
                for chunk in response.iter_bytes(chunk_size=1024*1024):
                    f.write(chunk)
            
            return filename
        except Exception as e:
            current_app.logger.error(f"Audio Generation Error: {str(e)}")
            raise
    
    def generate_chapter_audio(self, chapter_content, chapter_number):
        try:
            filename = f"chapter_{chapter_number}.mp3"
            return self.generate_audio(chapter_content, filename)
        except Exception as e:
            current_app.logger.error(f"Chapter Audio Generation Error: {str(e)}")
            raise
