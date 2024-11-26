from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import QuestionnaireResponse, Template, db
from flask_wtf.csrf import validate_csrf, ValidationError
import traceback

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
        # Check Content-Type header
        if not request.is_json:
            current_app.logger.error("Invalid Content-Type header for questionnaire response")
            return jsonify({
                'success': False,
                'message': 'Invalid request format. Expected JSON.'
            }), 400

        # Validate CSRF token
        try:
            csrf_token = request.headers.get('X-CSRFToken')
            if not csrf_token:
                current_app.logger.error("Missing CSRF token for questionnaire response")
                return jsonify({
                    'success': False,
                    'message': 'Missing CSRF token'
                }), 400
            validate_csrf(csrf_token)
        except ValidationError as e:
            current_app.logger.error(f"CSRF validation failed: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid CSRF token'
            }), 400

        try:
            data = request.get_json()
            if not isinstance(data, dict):
                return jsonify({
                    'success': False,
                    'message': 'Invalid response format'
                }), 400

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
        except ValueError as e:
            current_app.logger.error(f"Validation error: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except Exception as e:
            current_app.logger.error(f"Error submitting response: {str(e)}")
            db.session.rollback()
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
    if not request.is_json:
        current_app.logger.error(f"Non-JSON request received for response deletion {response_id}")
        return jsonify({
            'success': False,
            'message': 'Invalid request format. Expected JSON.'
        }), 400

    try:
        # Validate CSRF token
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token:
            current_app.logger.error(f"Missing CSRF token for response deletion {response_id}")
            return jsonify({
                'success': False,
                'message': 'Missing CSRF token'
            }), 400

        try:
            validate_csrf(csrf_token)
        except ValidationError as ve:
            current_app.logger.error(f"Invalid CSRF token for response deletion {response_id}: {str(ve)}")
            return jsonify({
                'success': False,
                'message': 'Invalid CSRF token'
            }), 400

        response = QuestionnaireResponse.query.get(response_id)
        if not response:
            current_app.logger.error(f"Response not found for deletion: {response_id}")
            return jsonify({
                'success': False,
                'message': 'Response not found'
            }), 404

        if response.status == 'deleted':
            current_app.logger.warning(f"Attempt to delete already deleted response: {response_id}")
            return jsonify({
                'success': False,
                'message': 'Response already deleted'
            }), 400

        response.status = 'deleted'  # Soft delete
        db.session.commit()
        
        current_app.logger.info(f"Successfully deleted response {response_id}")
        return jsonify({
            'success': True,
            'message': 'Response deleted successfully!'
        })

    except Exception as e:
        error_details = traceback.format_exc()
        current_app.logger.error(f"Error deleting response {response_id}:\n{error_details}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred while deleting the response. Please try again.'
        }), 500