from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import Template, QuestionnaireResponse, db

bp = Blueprint('questionnaires', __name__)

@bp.route('/questionnaires/list')
def list_responses():
    try:
        responses = QuestionnaireResponse.query.order_by(
            QuestionnaireResponse.created_at.desc()
        ).all()
        return render_template('questionnaires/list.html', responses=responses)
    except Exception as e:
        current_app.logger.error(f"Error listing responses: {str(e)}")
        flash('Error loading questionnaire responses. Please try again.', 'error')
        return redirect(url_for('templates.list_templates'))

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
                'redirect_url': url_for('questionnaires.list_responses')
            })

        except Exception as e:
            db.session.rollback()
            error_msg = f'Error submitting questionnaire response: {str(e)}'
            current_app.logger.error(error_msg)
            return jsonify({
                'success': False,
                'message': 'An error occurred while submitting your response. Please try again.',
                'error': str(e) if current_app.debug else None
            }), 500
    
    return render_template('questionnaires/respond.html', template=template)

def validate_responses(responses, template_sections):
    """Validate responses against template structure."""
    try:
        # Debug log the received data structure
        current_app.logger.debug(f"Validating responses: {responses}")
        current_app.logger.debug(f"Template sections: {template_sections}")
        
        # Validate each section
        for section_idx, section in enumerate(template_sections):
            section_key = str(section_idx)
            
            # Check if section exists in responses
            if section_key not in responses:
                current_app.logger.error(f"Missing section {section_key} in responses")
                return False
                
            section_responses = responses[section_key]
            
            # Validate each question in the section
            for question_idx, question in enumerate(section['questions']):
                question_key = str(question_idx)
                
                # Check if question exists in section responses
                if question_key not in section_responses:
                    current_app.logger.error(f"Missing question {question_key} in section {section_key}")
                    return False
                    
                # Get response value
                response_value = section_responses[question_key]
                
                # Validate response value based on question type
                if isinstance(response_value, str) and not response_value.strip():
                    current_app.logger.error(f"Empty response for section {section_key}, question {question_key}")
                    return False
                    
                # Additional type-specific validation could be added here
                
        return True
    except Exception as e:
        current_app.logger.error(f"Validation error: {str(e)}")
        return False

@bp.route('/questionnaires/response/<response_id>')
def view_response(response_id):
    try:
        response = QuestionnaireResponse.query.get_or_404(response_id)
        return render_template('questionnaires/view.html', response=response)
    except Exception as e:
        current_app.logger.error(f"Error viewing response {response_id}: {str(e)}")
        flash('Error loading questionnaire response. Please try again.', 'error')
        return redirect(url_for('templates.list_templates'))
