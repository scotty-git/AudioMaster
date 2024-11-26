from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Template, QuestionnaireResponse, db

bp = Blueprint('questionnaires', __name__)

@bp.route('/questionnaires/respond/<template_id>', methods=['GET', 'POST'])
def respond(template_id):
    template = Template.query.get_or_404(template_id)
    
    if request.method == 'POST':
        try:
            response = QuestionnaireResponse(
                template_id=template_id,
                responses=request.json
            )
            db.session.add(response)
            db.session.commit()
            flash('Response submitted successfully!', 'success')
            return redirect(url_for('questionnaires.view_response', response_id=response.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting response: {str(e)}', 'error')
    
    return render_template('questionnaires/respond.html', template=template)

@bp.route('/questionnaires/response/<response_id>')
def view_response(response_id):
    response = QuestionnaireResponse.query.get_or_404(response_id)
    return render_template('questionnaires/view.html', response=response)
