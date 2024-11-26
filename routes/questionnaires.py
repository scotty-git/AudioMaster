from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Template, QuestionnaireResponse, db

bp = Blueprint('questionnaires', __name__)

@bp.route('/questionnaires/respond/<template_id>', methods=['GET', 'POST'])
def respond(template_id):
    template = Template.query.get_or_404(template_id)
    
    if request.method == 'POST':
        try:
            # Validate request data
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Invalid request format. JSON expected.'
                }), 400

            data = request.get_json()
            
            # Validate responses against template structure
            if not validate_responses(data, template.sections):
                return jsonify({
                    'success': False,
                    'message': 'Invalid or incomplete responses'
                }), 400

            # Create response
            response = QuestionnaireResponse(
                template_id=template_id,
                responses=data,
                status='submitted'
            )
            db.session.add(response)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Response submitted successfully!',
                'redirect_url': url_for('questionnaires.view_response', response_id=response.id)
            })

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error submitting questionnaire response: {str(e)}')
            return jsonify({
                'success': False,
                'message': 'An error occurred while submitting your response'
            }), 500
    
    return render_template('questionnaires/respond.html', template=template)

def validate_responses(responses, template_sections):
    """Validate responses against template structure."""
    try:
        for section_idx, section in enumerate(template_sections):
            if str(section_idx) not in responses:
                return False
            
            section_responses = responses[str(section_idx)]
            for question_idx, _ in enumerate(section['questions']):
                if str(question_idx) not in section_responses:
                    return False
                if not section_responses[str(question_idx)].strip():
                    return False
        
        return True
    except (KeyError, AttributeError, TypeError):
        return False

@bp.route('/questionnaires/response/<response_id>')
def view_response(response_id):
    response = QuestionnaireResponse.query.get_or_404(response_id)
    return render_template('questionnaires/view.html', response=response)
