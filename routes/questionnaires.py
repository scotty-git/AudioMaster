from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import QuestionnaireResponse, db
from flask_wtf.csrf import validate_csrf, ValidationError

bp = Blueprint('questionnaires', __name__)

@bp.route('/questionnaires/list')
def list_responses():
    responses = QuestionnaireResponse.query.filter(
        QuestionnaireResponse.status != 'deleted'
    ).order_by(QuestionnaireResponse.created_at.desc()).all()
    return render_template('questionnaires/list.html', responses=responses)

@bp.route('/questionnaires/respond/<template_id>', methods=['GET', 'POST'])
def respond(template_id):
    template = Template.query.get_or_404(template_id)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
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
            current_app.logger.error(f"Error submitting response: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to submit response. Please try again.'
            }), 500
            
    return render_template('questionnaires/respond.html', template=template)

@bp.route('/questionnaires/response/<response_id>')
def view_response(response_id):
    try:
        response = QuestionnaireResponse.query.get_or_404(response_id)
        return render_template('questionnaires/view.html', response=response)
    except Exception as e:
        current_app.logger.error(f"Error viewing response {response_id}: {str(e)}")
        flash('Error loading questionnaire response. Please try again.', 'error')
        return redirect(url_for('templates.list_templates'))

@bp.route('/questionnaires/response/<response_id>/delete', methods=['POST'])
def delete_response(response_id):
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({
                'success': False,
                'message': 'Invalid CSRF token'
            }), 400

        response = QuestionnaireResponse.query.get_or_404(response_id)
        response.status = 'deleted'  # Soft delete
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Response deleted successfully!'
        })
    except Exception as e:
        current_app.logger.error(f"Error deleting response {response_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error deleting response. Please try again.'
        }), 500