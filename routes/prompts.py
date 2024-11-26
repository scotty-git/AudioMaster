from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import PromptTemplate, db
from flask_wtf.csrf import validate_csrf, ValidationError

bp = Blueprint('prompts', __name__)

@bp.route('/prompts')
def list_prompts():
    prompts = PromptTemplate.query.filter_by(is_active=True).all()
    return render_template('prompts/list.html', prompts=prompts)

@bp.route('/prompts/create', methods=['GET', 'POST'])
def create_prompt():
    if request.method == 'POST':
        try:
            data = request.get_json()
            prompt = PromptTemplate(
                name=data['name'],
                description=data['description'],
                type=data['type'],
                template_content=data['template_content'],
                variables=data.get('variables', {})
            )
            db.session.add(prompt)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Prompt template created successfully!',
                'redirect_url': url_for('prompts.view_prompt', prompt_id=prompt.id)
            })
        except Exception as e:
            current_app.logger.error(f"Error creating prompt template: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to create prompt template. Please try again.'
            }), 500
            
    return render_template('prompts/create.html')

@bp.route('/prompts/<prompt_id>')
def view_prompt(prompt_id):
    prompt = PromptTemplate.query.get_or_404(prompt_id)
    return render_template('prompts/view.html', prompt=prompt)

@bp.route('/prompts/<prompt_id>/edit', methods=['GET', 'POST'])
def edit_prompt(prompt_id):
    prompt = PromptTemplate.query.get_or_404(prompt_id)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            prompt.name = data['name']
            prompt.description = data['description']
            prompt.type = data['type']
            prompt.template_content = data['template_content']
            prompt.variables = data.get('variables', {})
            
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Prompt template updated successfully!',
                'redirect_url': url_for('prompts.view_prompt', prompt_id=prompt.id)
            })
        except Exception as e:
            current_app.logger.error(f"Error updating prompt template: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to update prompt template. Please try again.'
            }), 500
            
    return render_template('prompts/edit.html', prompt=prompt)

@bp.route('/prompts/<prompt_id>/delete', methods=['POST'])
def delete_prompt(prompt_id):
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({
                'success': False,
                'message': 'Invalid CSRF token'
            }), 400

        prompt = PromptTemplate.query.get_or_404(prompt_id)
        prompt.is_active = False  # Soft delete
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Prompt template deleted successfully!'
        })
    except Exception as e:
        current_app.logger.error(f"Error deleting prompt template {prompt_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error deleting prompt template. Please try again.'
        }), 500
