from flask import Blueprint, render_template, current_app, request, jsonify, make_response
from flask_wtf.csrf import CSRFProtect
import inspect
import os
import importlib
import sys
from routes import prompts, templates, questionnaires, audiobooks, outlines
from models import db
import datetime
import flask
import sqlalchemy

docs = Blueprint('docs', __name__)
csrf = CSRFProtect()

def get_routes_info():
    routes = []
    try:
        # Import all route modules dynamically
        route_modules = ['templates', 'prompts', 'questionnaires', 'outlines', 'audiobooks']
        for module_name in route_modules:
            try:
                module = importlib.import_module(f'routes.{module_name}')
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj):
                        # Collect route information dynamically
                        route_info = {
                            'name': name,
                            'module': module_name,
                            'methods': [method for method in ['GET', 'POST', 'PUT', 'DELETE'] if hasattr(obj, method.lower())],
                            'url_rules': [rule.rule for rule in current_app.url_map.bind('').iter_rules() if rule.endpoint.startswith(module_name)]
                        }
                        routes.append(route_info)
            except ImportError as e:
                current_app.logger.error(f"Could not import {module_name}: {e}")
    except Exception as e:
        current_app.logger.error(f"Error getting routes: {e}")
    return routes

def get_template_info():
    template_info = {
        'prompts': ['list.html', 'create.html', 'edit.html', 'view.html', 'versions.html'],
        'templates': ['list.html', 'create.html', 'edit.html', 'view.html'],
        'questionnaires': ['list.html', 'respond.html', 'view.html'],
        'audiobooks': ['list.html'],
        'outlines': ['list.html', 'generate.html', 'view.html']
    }
    try:
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        for root, _, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    relative_path = os.path.relpath(os.path.join(root, file), template_dir)
                    if relative_path.startswith('docs/'):
                        continue
                    for category, templates in template_info.items():
                        if relative_path.startswith(category + '/'):
                            if relative_path not in templates:
                                templates.append(relative_path)
    except Exception as e:
        current_app.logger.error(f"Error collecting template info: {e}")
    return template_info

def get_database_info():
    try:
        # Dynamically collect database model information
        models_module = importlib.import_module('models')
        tables = []
        for name, obj in inspect.getmembers(models_module):
            if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
                table_info = {
                    'name': name,
                    'table_name': obj.__tablename__,
                    'columns': [column.name for column in obj.__table__.columns]
                }
                tables.append(table_info)
        return tables
    except Exception as e:
        current_app.logger.error(f"Error collecting database info: {e}")
        return []

@docs.route('/debug_headers', methods=['GET'])
def debug_headers():
    """Diagnostic route to print out all request headers."""
    headers = dict(request.headers)
    current_app.logger.info(f"Debug Headers: {headers}")
    return jsonify({
        'headers': headers,
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr
    }), 200

@docs.route('/docs', methods=['GET'])
def documentation():
    try:
        routes_info = get_routes_info()
        template_info = get_template_info()
        database_info = get_database_info()
        
        # Collect system metadata
        system_info = {
            'python_version': sys.version,
            'flask_version': flask.__version__,
            'sqlalchemy_version': sqlalchemy.__version__,
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'debug_mode': current_app.config.get('DEBUG', False)
        }
        
        last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return render_template(
            'docs/docs.html', 
            routes_info=routes_info, 
            template_info=template_info, 
            database_info=database_info,
            system_info=system_info,
            last_updated=last_updated
        )
    except Exception as e:
        current_app.logger.error(f"Documentation route error: {e}", exc_info=True)
        return f"Error generating documentation: {e}", 500
