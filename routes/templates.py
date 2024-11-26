from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models import Template, db
from datetime import datetime

bp = Blueprint('templates', __name__)

@bp.route('/templates')
def list_templates():
    templates = Template.query.filter_by(is_active=True).all()
    return render_template('templates/list.html', templates=templates)

@bp.route('/templates/create', methods=['GET', 'POST'])
def create_template():
    if request.method == 'POST':
        try:
            if request.is_json:
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
                    'redirect_url': url_for('templates.list_templates')
                })
            else:
                # Handle traditional form submission for non-JS fallback
                template = Template(
                    title=request.form['title'],
                    description=request.form['description'],
                    sections=[]  # Initialize with empty sections for form-based submission
                )
                db.session.add(template)
                db.session.commit()
                flash('Template created successfully!', 'success')
                return redirect(url_for('templates.list_templates'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating template: {str(e)}')
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Error creating template'
                }), 500
            flash(f'Error creating template: {str(e)}', 'error')
            return redirect(url_for('templates.create_template'))
    
    return render_template('templates/create.html')

@bp.route('/templates/<template_id>')
def view_template(template_id):
    template = Template.query.get_or_404(template_id)
    return render_template('templates/view.html', template=template)


@bp.route('/templates/<template_id>/delete', methods=['POST'])
def delete_template(template_id):
    try:
        template = Template.query.get_or_404(template_id)
        template.is_active = False  # Soft delete
        db.session.commit()
        flash('Template deleted successfully!', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting template {template_id}: {str(e)}")
        flash('Error deleting template. Please try again.', 'error')
        db.session.rollback()
    return redirect(url_for('templates.list_templates'))
