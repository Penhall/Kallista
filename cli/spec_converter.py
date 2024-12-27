# cli/spec_converter.py

class SpecificationConverter:
    def __init__(self):
        self.architecture_patterns = {
            'kanban': ['MVVM', 'Repository'],
            'dashboard': ['MVVM', 'Observer'],
            'crud': ['MVVM', 'Repository', 'UnitOfWork'],
            'document': ['MVVM', 'Command'],
            'report': ['MVVM', 'Template'],
            'custom': ['MVVM']
        }
        
        self.default_layers = [
            'Presentation',
            'Domain',
            'Data',
            'Infrastructure'
        ]

    def convert_to_project_structure(self, specs):
        """Converte especificações brutas em estrutura de projeto"""
        project_structure = {
            'type': specs['type'],
            'metadata': {
                'name': specs['name'],
                'description': specs.get('description', ''),
                'authentication': specs.get('authentication', False),
                'database': specs.get('database', False)
            },
            'architecture': {
                'patterns': self.architecture_patterns[specs['type']],
                'layers': self.default_layers
            },
            'features': self._get_features_by_type(specs)
        }
        
        return project_structure

    def _get_features_by_type(self, specs):
        """Retorna features específicas baseadas no tipo do projeto"""
        if specs['type'] == 'kanban':
            return self._get_kanban_features(specs)
        elif specs['type'] == 'dashboard':
            return self._get_dashboard_features(specs)
        # ... outros tipos
        
        return {}

    def _get_kanban_features(self, specs):
        return {
            'board': {
                'columns': specs.get('columns', ['Todo', 'In Progress', 'Done']),
                'cards': {
                    'fields': specs.get('card_fields', ['title', 'description']),
                    'actions': ['create', 'edit', 'move', 'delete']
                }
            },
            'components': {
                'board_view': True,
                'card_editor': True,
                'drag_drop': True,
                'filters': True
            }
        }

    def _get_dashboard_features(self, specs):
        return {
            'data': {
                'source': specs.get('data_source', ''),
                'update_interval': specs.get('update_interval', '60'),
                'charts': specs.get('charts', [])
            },
            'components': {
                'chart_container': True,
                'filters': True,
                'export': True,
                'refresh': True
            }
        }