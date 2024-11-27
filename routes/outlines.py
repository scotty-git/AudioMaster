from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import QuestionnaireResponse, BookOutline, db
from services.ai_service import AIService
from flask_wtf.csrf import validate_csrf, ValidationError

bp = Blueprint('outlines', __name__)

@bp.route('/outlines', methods=['GET'])
def list_outlines():
    outlines = BookOutline.query.order_by(BookOutline.created_at.desc()).all()
    return render_template('outlines/list.html', outlines=outlines)

@bp.route('/outlines/generate/<response_id>', methods=['POST'])
def generate_outline(response_id):
    # Validate CSRF token
    try:
        if request.is_json:
            validate_csrf(request.headers.get('X-CSRFToken'))
        else:
            validate_csrf(request.form.get('csrf_token'))
    except ValidationError:
        current_app.logger.error("CSRF validation failed for outline generation")
        if request.is_json:
            return jsonify({
                'success': False,
                'message': 'Invalid CSRF token. Please refresh the page and try again.'
            }), 400
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('questionnaires.view_response', response_id=response_id))

    try:
        response = QuestionnaireResponse.query.get_or_404(response_id)
        
        # Check if response is in valid state
        if response.status != 'submitted':
            raise ValueError(f"Invalid response status: {response.status}. Response must be in 'submitted' state.")
            
        ai_service = AIService()
        current_app.logger.info(f"Starting outline generation for response {response_id}")
        
        # Update response status to processing
        response.status = 'processing'
        db.session.commit()
        
        try:
            outline_data = ai_service.generate_outline(response.responses)
            current_app.logger.info(f"AI outline generation completed for response {response_id}")
            
            outline = BookOutline(
                questionnaire_id=response_id,
                chapters=outline_data,
                status='draft'
            )
            db.session.add(outline)
            db.session.commit()
            current_app.logger.info(f"Outline saved to database with id {outline.id}")
            
            success_response = {
                'success': True,
                'message': 'Outline generated successfully!',
                'redirect_url': url_for('outlines.view_outline', outline_id=outline.id)
            }
            
            return jsonify(success_response) if request.is_json else redirect(success_response['redirect_url'])
            
        except ValueError as e:
            error_msg = str(e)
            if 'validation' in error_msg.lower():
                error_msg = f"AI response validation failed: {error_msg}"
            elif 'json' in error_msg.lower():
                error_msg = "Invalid response format from AI service. Please try again."
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = str(e)
            if 'timeout' in error_msg.lower():
                error_msg = "Request timed out. The outline generation is taking longer than expected. Please try again."
            elif 'rate limit' in error_msg.lower():
                error_msg = "AI service is currently busy. Please wait a few moments and try again."
            raise Exception(error_msg)
            
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Validation error during outline generation: {str(e)}")
        error_response = {
            'success': False,
            'message': str(e),
            'error_type': 'validation_error'
        }
        return jsonify(error_response) if request.is_json else render_template('error.html', error=str(e)), 400
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating outline: {str(e)}")
        error_response = {
            'success': False,
            'message': str(e),
            'error_type': 'system_error'
        }
        return jsonify(error_response) if request.is_json else render_template('error.html', error=str(e)), 500
        
    finally:
        if 'response' in locals():
            response.status = 'submitted'  # Reset status if error occurred
            db.session.commit()
    
    # Handle regular POST request
    try:
        current_app.logger.info(f"Starting outline generation for response {response_id}")
        outline_data = ai_service.generate_outline(response.responses)
        
        outline = BookOutline(
            questionnaire_id=response_id,
            chapters=outline_data,
            status='draft'
        )
        db.session.add(outline)
        db.session.commit()
        current_app.logger.info(f"Outline saved to database with id {outline.id}")
        
        flash('Outline generated successfully!', 'success')
        return redirect(url_for('outlines.view_outline', outline_id=outline.id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating outline: {str(e)}")
        flash('Error generating outline. Please try again.', 'error')
        return redirect(url_for('questionnaires.view_response', response_id=response_id))

@bp.route('/outlines/generate/new', methods=['GET'])
def new_outline():
    # Render a page to select a questionnaire response for outline generation
    responses = QuestionnaireResponse.query.filter_by(status='submitted').all()
    return render_template('outlines/generate.html', responses=responses)

@bp.route('/outlines/<outline_id>', methods=['GET'])
def view_outline(outline_id):
    outline = BookOutline.query.get_or_404(outline_id)
    return render_template('outlines/view.html', outline=outline)
