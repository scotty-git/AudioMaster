from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import BookOutline, Audiobook, db
from services.audio_service import AudioService
from services.ai_service import AIService

bp = Blueprint('audiobooks', __name__)

@bp.route('/audiobooks/generate/<outline_id>', methods=['POST'])
def generate_audiobook(outline_id):
    outline = BookOutline.query.get_or_404(outline_id)
    ai_service = AIService()
    audio_service = AudioService()
    
    try:
        audiobook = Audiobook(
            outline_id=outline_id,
            chapter_files={},
            status='generating'
        )
        db.session.add(audiobook)
        db.session.commit()
        
        chapter_files = {}
        for chapter in outline.chapters['chapters']:
            # Generate detailed chapter content
            content = ai_service.generate_chapter_content(chapter)
            
            # Convert to audio
            audio_file = audio_service.generate_chapter_audio(
                content, 
                chapter['number']
            )
            
            chapter_files[str(chapter['number'])] = audio_file
        
        audiobook.chapter_files = chapter_files
        audiobook.status = 'completed'
        db.session.commit()
        
        flash('Audiobook generated successfully!', 'success')
        return redirect(url_for('audiobooks.view_audiobook', audiobook_id=audiobook.id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error generating audiobook: {str(e)}', 'error')
        return redirect(url_for('outlines.view_outline', outline_id=outline_id))

@bp.route('/audiobooks/<audiobook_id>')
def view_audiobook(audiobook_id):
    audiobook = Audiobook.query.get_or_404(audiobook_id)
    return render_template('audiobooks/view.html', audiobook=audiobook)
