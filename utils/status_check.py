from typing import Dict, List
import importlib
import inspect
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class FeatureStatus(Enum):
    IMPLEMENTED = "✅"
    IN_PROGRESS = "🚧"
    PLANNED = "⏳"

@dataclass
class FeatureInfo:
    name: str
    status: FeatureStatus
    description: str
    last_updated: str

class StatusChecker:
    def __init__(self):
        self.features: Dict[str, FeatureInfo] = {}
        self.api_endpoints: List[str] = []
        self.template_types: List[str] = []
        self.components: Dict[str, FeatureStatus] = {}

    def check_feature_implementation(self, module_name: str) -> FeatureStatus:
        try:
            module = importlib.import_module(module_name)
            # Check if module has required functions/classes
            if hasattr(module, '__all__'):
                return FeatureStatus.IMPLEMENTED
            return FeatureStatus.IN_PROGRESS
        except ImportError:
            return FeatureStatus.PLANNED

    def scan_templates(self) -> Dict[str, List[str]]:
        template_dir = Path("templates")
        template_types = {}
        
        for path in template_dir.glob("**/*.html"):
            category = path.parent.name
            if category not in template_types:
                template_types[category] = []
            template_types[category].append(path.name)
            
        return template_types

    def check_api_endpoints(self) -> List[Dict[str, str]]:
        endpoints = []
        routes_dir = Path("routes")
        
        for path in routes_dir.glob("*.py"):
            try:
                module_name = f"routes.{path.stem}"
                module = importlib.import_module(module_name)
                
                for name, obj in inspect.getmembers(module):
                    if hasattr(obj, 'view_class'):
                        endpoints.append({
                            'name': name,
                            'module': module_name,
                            'type': 'class-based'
                        })
                    elif hasattr(obj, '__call__') and hasattr(obj, 'route'):
                        endpoints.append({
                            'name': name,
                            'module': module_name,
                            'type': 'function'
                        })
            except ImportError:
                continue
                
        return endpoints

    def check_front_end_components(self) -> Dict[str, FeatureStatus]:
        components = {
            'Navigation': FeatureStatus.IMPLEMENTED,
            'Template Editor': self.check_feature_implementation('templates.edit'),
            'Prompt Manager': self.check_feature_implementation('prompts'),
            'Version Control': self.check_feature_implementation('models.version'),
            'User Authentication': FeatureStatus.PLANNED
        }
        return components

    def run_all_checks(self) -> Dict:
        return {
            'features': {
                'Templates': FeatureStatus.IMPLEMENTED,
                'Prompts': FeatureStatus.IMPLEMENTED,
                'Questionnaires': FeatureStatus.IN_PROGRESS,
                'Audiobooks': FeatureStatus.PLANNED,
                'Documentation': FeatureStatus.IN_PROGRESS
            },
            'template_types': self.scan_templates(),
            'api_endpoints': self.check_api_endpoints(),
            'components': self.check_front_end_components()
        }
