from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import PromptTemplate, PromptTemplateVersion, db
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('prompts', __name__)

@bp.route('/prompts')
def list_prompts():
    prompts = PromptTemplate.query.all()
    
    if not prompts:
        # Create default prompt template
        default_prompt = PromptTemplate(
            name="Default Book Outline Generator",
            description="Default template for generating book outlines from questionnaire responses",
            type="outline",
            template_content='''Based on the following questionnaire responses, create a detailed book outline optimized for audio format and engaging listening experience:

{responses}

Please create a well-structured outline that:
1. Maintains a clear narrative flow between chapters
2. Ensures each chapter builds upon previous content
3. Includes transition points between major topics
4. Considers the audio listening experience

Create a JSON response with the following structure:
{
    "title": "Book Title",
    "chapters": [
        {
            "number": 1,
            "title": "Chapter Title",
            "summary": "Detailed chapter summary including main themes and flow",
            "key_points": ["Specific key point 1", "Specific key point 2"],
            "estimated_duration": "15-20 minutes"
        }
    ]
}

Ensure each chapter is substantial enough for audio content but not too long for comfortable listening.''',
            variables={"responses": "JSON object containing questionnaire responses"}
        )
        db.session.add(default_prompt)
        db.session.commit()
        prompts = [default_prompt]
        
    return render_template('prompts/list.html', prompts=prompts)

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
            
            # Create a new version before updating
            prompt.create_version(current_app.config.get('DEFAULT_USER_ID'))
            
            # Update the prompt
            prompt.name = data['name']
            prompt.description = data['description']
            prompt.type = data['type']
            prompt.template_content = data['template_content']
            prompt.variables = data.get('variables', {})
            prompt.is_active = data.get('is_active', True)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Prompt template updated successfully!',
                'redirect_url': url_for('prompts.view_prompt', prompt_id=prompt.id)
            })
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating prompt template: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Database error occurred. Please try again.'
            }), 500
        except Exception as e:
            current_app.logger.error(f"Error updating prompt template: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to update prompt template. Please try again.'
            }), 500
            
    return render_template('prompts/edit.html', prompt=prompt)

@bp.route('/prompts/<prompt_id>/versions/<int:version>')
def view_version(prompt_id, version):
    prompt = PromptTemplate.query.get_or_404(prompt_id)
    version = prompt.versions.filter_by(version=version).first_or_404()
    return render_template('prompts/version.html', prompt=prompt, version=version)

@bp.route('/prompts/<prompt_id>/versions')
def list_versions(prompt_id):
    prompt = PromptTemplate.query.get_or_404(prompt_id)
    versions = prompt.versions.order_by(PromptTemplateVersion.version.desc()).all()
    return render_template('prompts/versions.html', prompt=prompt, versions=versions)

@bp.route('/prompts/<prompt_id>/restore/<int:version>', methods=['POST'])
def restore_version(prompt_id, version):
    try:
        prompt = PromptTemplate.query.get_or_404(prompt_id)
        old_version = prompt.versions.filter_by(version=version).first_or_404()
        
        # Create a new version of current state
        prompt.create_version(current_app.config.get('DEFAULT_USER_ID'))
        
        # Restore the old version's content
        prompt.name = old_version.name
        prompt.description = old_version.description
        prompt.type = old_version.type
        prompt.template_content = old_version.template_content
        prompt.variables = old_version.variables
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully restored version {version}',
            'redirect_url': url_for('prompts.view_prompt', prompt_id=prompt.id)
        })
    except Exception as e:
        current_app.logger.error(f"Error restoring version: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to restore version. Please try again.'
        }), 500

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
                variables=data.get('variables', {}),
                user_id=current_app.config.get('DEFAULT_USER_ID')
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

@bp.route('/prompts/<prompt_id>/delete', methods=['POST'])
def delete_prompt(prompt_id):
    try:
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
