from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import Template, db
from flask_wtf.csrf import validate_csrf, ValidationError

bp = Blueprint('templates', __name__)

@bp.route('/templates')
def list_templates():
    templates = Template.query.filter_by(is_active=True).all()
    return render_template('templates/list.html', templates=templates)

@bp.route('/templates/create', methods=['GET', 'POST'])
def create_template():
    if request.method == 'POST':
        try:
            data = request.get_json()
            template = Template(
                title=data['title'],
                description=data['description'],
                sections=data['sections']
            )
            db.session.add(template)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Template created successfully!',
                'redirect_url': url_for('templates.view_template', template_id=template.id)
            })
        except Exception as e:
            current_app.logger.error(f"Error creating template: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to create template. Please try again.'
            }), 500
            
    return render_template('templates/create.html')

@bp.route('/templates/<template_id>')
def view_template(template_id):
    template = Template.query.get_or_404(template_id)
    return render_template('templates/view.html', template=template)

@bp.route('/templates/<template_id>/delete', methods=['POST'])
def delete_template(template_id):
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({
                'success': False,
                'message': 'Invalid CSRF token'
            }), 400

        template = Template.query.get_or_404(template_id)
        template.is_active = False  # Soft delete
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Template deleted successfully!'
        })
    except Exception as e:
        current_app.logger.error(f"Error deleting template {template_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error deleting template. Please try again.'
        }), 500
