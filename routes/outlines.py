from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import QuestionnaireResponse, BookOutline, db
from services.ai_service import AIService
from flask_wtf.csrf import validate_csrf, ValidationError

bp = Blueprint('outlines', __name__)

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
                'message': 'Invalid CSRF token'
            }), 400
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('questionnaires.view_response', response_id=response_id))
    response = QuestionnaireResponse.query.get_or_404(response_id)
    ai_service = AIService()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX request
        try:
            current_app.logger.info(f"Starting outline generation for response {response_id}")
            
            # Update response status to processing
            response.status = 'processing'
            db.session.commit()
            
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
            
            return jsonify({
                'success': True,
                'message': 'Outline generated successfully!',
                'redirect_url': url_for('outlines.view_outline', outline_id=outline.id)
            })
            
        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f"Validation error during outline generation: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error generating outline: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred while generating the outline. Please try again.'
            }), 500
    
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

@bp.route('/outlines/<outline_id>')
def view_outline(outline_id):
    outline = BookOutline.query.get_or_404(outline_id)
    return render_template('outlines/view.html', outline=outline)
