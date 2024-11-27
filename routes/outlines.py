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
    """Generate a book outline from a questionnaire response."""
    # Always return JSON responses for consistency
    if not request.is_json:
        return jsonify({
            'success': False,
            'message': 'Invalid request format. Expected JSON.'
        }), 400

    # Validate CSRF token
    try:
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token:
            current_app.logger.error("Missing CSRF token for outline generation")
            return jsonify({
                'success': False,
                'message': 'Missing security token. Please refresh the page and try again.'
            }), 400
            
        validate_csrf(csrf_token)
    except ValidationError:
        current_app.logger.error("CSRF validation failed for outline generation")
        return jsonify({
            'success': False,
            'message': 'Invalid security token. Please refresh the page and try again.'
        }), 400

    try:
        # Get and validate questionnaire response
        response = QuestionnaireResponse.query.get_or_404(response_id)
        if not response:
            return jsonify({
                'success': False,
                'message': 'Questionnaire response not found.'
            }), 404
            
        # Check if response is in valid state
        if response.status != 'submitted':
            return jsonify({
                'success': False,
                'message': f'Invalid response status: {response.status}. Response must be submitted first.'
            }), 400
            
        # Initialize AI service and start generation
        ai_service = AIService()
        current_app.logger.info(f"Starting outline generation for response {response_id}")
        
        # Update response status to processing
        response.status = 'processing'
        db.session.commit()
        
        try:
            # Generate outline using AI service
            outline_data = ai_service.generate_outline(response.responses)
            current_app.logger.info(f"AI outline generation completed for response {response_id}")
            
            # Create and save outline
            outline = BookOutline(
                questionnaire_id=response_id,
                chapters=outline_data,
                status='draft'
            )
            db.session.add(outline)
            db.session.commit()
            current_app.logger.info(f"Outline saved to database with id {outline.id}")
            
            return jsonify({
                'success': True,
                'message': 'Outline generated successfully!',
                'redirect_url': url_for('outlines.view_outline', outline_id=outline.id)
            })
            
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
        return jsonify({
            'success': False,
            'message': str(e),
            'error_type': 'validation_error'
        }), 400
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating outline: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'error_type': 'system_error'
        }), 500
        
    finally:
        if 'response' in locals():
            response.status = 'submitted'  # Reset status if error occurred
            try:
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Error resetting response status: {str(e)}")
                db.session.rollback()

@bp.route('/outlines/generate/new', methods=['GET'])
def new_outline():
    # Render a page to select a questionnaire response for outline generation
    responses = QuestionnaireResponse.query.filter_by(status='submitted').all()
    return render_template('outlines/generate.html', responses=responses)

@bp.route('/outlines/<outline_id>', methods=['GET'])
def view_outline(outline_id):
    outline = BookOutline.query.get_or_404(outline_id)
    return render_template('outlines/view.html', outline=outline)
