from flask import Blueprint, render_template, request, flash, redirect, url_for
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
            template = Template(
                title=request.form['title'],
                description=request.form['description'],
                sections=request.json['sections']
            )
            db.session.add(template)
            db.session.commit()
            flash('Template created successfully!', 'success')
            return redirect(url_for('templates.list_templates'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating template: {str(e)}', 'error')
    
    return render_template('templates/create.html')

@bp.route('/templates/<template_id>')
def view_template(template_id):
    template = Template.query.get_or_404(template_id)
    return render_template('templates/view.html', template=template)
