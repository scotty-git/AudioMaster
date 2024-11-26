from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import QuestionnaireResponse, BookOutline, db
from services.ai_service import AIService

bp = Blueprint('outlines', __name__)

@bp.route('/outlines/generate/<response_id>', methods=['POST'])
def generate_outline(response_id):
    response = QuestionnaireResponse.query.get_or_404(response_id)
    ai_service = AIService()
    
    try:
        outline_data = ai_service.generate_outline(response.responses)
        outline = BookOutline(
            questionnaire_id=response_id,
            chapters=outline_data,
            status='draft'
        )
        db.session.add(outline)
        db.session.commit()
        flash('Outline generated successfully!', 'success')
        return redirect(url_for('outlines.view_outline', outline_id=outline.id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error generating outline: {str(e)}', 'error')
        return redirect(url_for('questionnaires.view_response', response_id=response_id))

@bp.route('/outlines/<outline_id>')
def view_outline(outline_id):
    outline = BookOutline.query.get_or_404(outline_id)
    return render_template('outlines/view.html', outline=outline)
