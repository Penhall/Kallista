# tests/system/test_system.py
import unittest
import asyncio
from pathlib import Path
import json
import shutil
from datetime import datetime

from kallista.core import KallistaSystem
from agents.core.architect_agent import ArchitectAgent
from agents.specialized.wpf_agent import WPFAgent
from agents.specialized.database_agent import DatabaseAgent
from workflows.workflow_manager import WorkflowManager
from tools.code.generator import CodeGenerator
from tools.database.schema_generator import SchemaGenerator

class TestKallistaSystem(unittest.TestCase):
    def setUp(self):
        """Setup para os testes de sistema"""
        self.config = {
            'base_dir': 'test_system',
            'templates_dir': 'test_templates',
            'output_dir': 'test_output',
            'logs_dir': 'test_logs'
        }
        
        # Cria diretórios necessários
        for dir_name in self.config.values():
            Path(dir_name).mkdir(exist_ok=True)
        
        # Inicializa o sistema
        self.system = KallistaSystem(self.config)
        
        # Inicializa componentes para testes específicos
        self.workflow_manager = WorkflowManager()
        self.code_generator = CodeGenerator()
        self.schema_generator = SchemaGenerator()

    def tearDown(self):
        """Limpeza após os testes"""
        # Remove diretórios de teste
        for dir_name in self.config.values():
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)

    async def test_complete_wpf_project_creation(self):
        """Testa criação completa de um projeto WPF"""
        # Configuração do projeto
        project_config = {
            'name': 'TestWPFProject',
            'type': 'WPF',
            'features': [
                'user_authentication',
                'data_persistence',
                'reporting'
            ],
            'ui': {
                'theme': 'modern',
                'forms': [
                    {
                        'name': 'Login',
                        'fields': ['username', 'password']
                    },
                    {
                        'name': 'Dashboard',
                        'components': ['user_list', 'report_viewer']
                    }
                ]
            },
            'database': {
                'type': 'SQL_Server',
                'entities': [
                    {
                        'name': 'User',
                        'properties': [
                            {'name': 'Id', 'type': 'int', 'key': True},
                            {'name': 'Username', 'type': 'string'},
                            {'name': 'Email', 'type': 'string'},
                            {'name': 'PasswordHash', 'type': 'string'}
                        ]
                    },
                    {
                        'name': 'Report',
                        'properties': [
                            {'name': 'Id', 'type': 'int', 'key': True},
                            {'name': 'Name', 'type': 'string'},
                            {'name': 'CreatedAt', 'type': 'datetime'},
                            {'name': 'Data', 'type': 'json'}
                        ]
                    }
                ]
            }
        }

        # Inicia criação do projeto
        result = await self.system.create_project(project_config)
        
        # Verifica resultado geral
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['project_id'])
        
        project_dir = Path(result['project_path'])
        
        # 1. Verifica estrutura do projeto
        self.assertTrue(project_dir.exists())
        self.assertTrue((project_dir / 'TestWPFProject.sln').exists())
        self.assertTrue((project_dir / 'TestWPFProject.UI').exists())
        self.assertTrue((project_dir / 'TestWPFProject.Core').exists())
        self.assertTrue((project_dir / 'TestWPFProject.Data').exists())
        
        # 2. Verifica arquivos UI
        ui_dir = project_dir / 'TestWPFProject.UI'
        self.assertTrue((ui_dir / 'Views/LoginView.xaml').exists())
        self.assertTrue((ui_dir / 'Views/DashboardView.xaml').exists())
        self.assertTrue((ui_dir / 'ViewModels/LoginViewModel.cs').exists())
        self.assertTrue((ui_dir / 'ViewModels/DashboardViewModel.cs').exists())
        
        # 3. Verifica arquivos de banco de dados
        data_dir = project_dir / 'TestWPFProject.Data'
        self.assertTrue((data_dir / 'Models/User.cs').exists())
        self.assertTrue((data_dir / 'Models/Report.cs').exists())
        self.assertTrue((data_dir / 'Context/ApplicationDbContext.cs').exists())
        
        # 4. Verifica arquivos de configuração
        self.assertTrue((ui_dir / 'App.config').exists())
        self.assertTrue((ui_dir / 'appsettings.json').exists())
        
        # 5. Verifica geração de código
        # Verifica LoginView.xaml
        login_view = (ui_dir / 'Views/LoginView.xaml').read_text()
        self.assertIn('TextBox', login_view)
        self.assertIn('PasswordBox', login_view)
        self.assertIn('Login', login_view)
        
        # Verifica LoginViewModel.cs
        login_vm = (ui_dir / 'ViewModels/LoginViewModel.cs').read_text()
        self.assertIn('LoginCommand', login_vm)
        self.assertIn('INavigationService', login_vm)
        self.assertIn('IAuthenticationService', login_vm)
        
        # Verifica User.cs
        user_model = (data_dir / 'Models/User.cs').read_text()
        self.assertIn('public int Id', user_model)
        self.assertIn('public string Username', user_model)
        self.assertIn('public string PasswordHash', user_model)
        
        # 6. Verifica configurações
        app_config = (ui_dir / 'appsettings.json').read_text()
        config_data = json.loads(app_config)
        self.assertIn('ConnectionStrings', config_data)
        self.assertIn('Authentication', config_data)
        
        # 7. Verifica configuração do Entity Framework
        db_context = (data_dir / 'Context/ApplicationDbContext.cs').read_text()
        self.assertIn('DbSet<User>', db_context)
        self.assertIn('DbSet<Report>', db_context)
        self.assertIn('OnModelCreating', db_context)
        
        # 8. Verifica logs de criação
        log_file = Path(self.config['logs_dir']) / 'project_creation.log'
        self.assertTrue(log_file.exists())
        log_content = log_file.read_text()
        self.assertIn('Project creation started', log_content)
        self.assertIn('Project creation completed', log_content)
        
        # 9. Verifica arquivos de teste
        test_dir = project_dir / 'TestWPFProject.Tests'
        self.assertTrue(test_dir.exists())
        self.assertTrue((test_dir / 'ViewModels/LoginViewModelTests.cs').exists())
        self.assertTrue((test_dir / 'Services/AuthenticationServiceTests.cs').exists())

    async def test_project_modification(self):
        """Testa modificação de um projeto existente"""
        # Primeiro cria um projeto básico
        initial_config = {
            'name': 'ModificationTest',
            'type': 'WPF',
            'features': ['user_authentication']
        }
        
        initial_result = await self.system.create_project(initial_config)
        project_dir = Path(initial_result['project_path'])
        
        # Configuração da modificação
        modification_config = {
            'add_features': ['data_export', 'reporting'],
            'add_entities': [
                {
                    'name': 'Report',
                    'properties': [
                        {'name': 'Id', 'type': 'int', 'key': True},
                        {'name': 'Name', 'type': 'string'},
                        {'name': 'Data', 'type': 'json'}
                    ]
                }
            ],
            'add_views': [
                {
                    'name': 'ReportViewer',
                    'type': 'Page',
                    'components': ['report_list', 'export_button']
                }
            ]
        }
        
        # Executa modificação
        mod_result = await self.system.modify_project(
            initial_result['project_id'],
            modification_config
        )
        
        # Verifica modificações
        self.assertTrue(mod_result['success'])
        
        # Verifica novos arquivos
        self.assertTrue(
            (project_dir / 'ModificationTest.UI/Views/ReportViewer.xaml').exists()
        )
        self.assertTrue(
            (project_dir / 'ModificationTest.Data/Models/Report.cs').exists()
        )
        
        # Verifica atualizações
        db_context = (project_dir / 'ModificationTest.Data/Context/ApplicationDbContext.cs').read_text()
        self.assertIn('DbSet<Report>', db_context)
        
        # Verifica logs de modificação
        mod_log = Path(self.config['logs_dir']) / 'project_modification.log'
        self.assertTrue(mod_log.exists())
        log_content = mod_log.read_text()
        self.assertIn('Project modification started', log_content)
        self.assertIn('Project modification completed', log_content)

    async def test_project_validation(self):
        """Testa validação de projeto"""
        # Cria projeto com problemas conhecidos
        project_config = {
            'name': 'ValidationTest',
            'type': 'WPF',
            'features': ['user_authentication'],
            'ui': {
                'forms': [
                    {
                        'name': 'Login',
                        'fields': ['username', 'password']
                    }
                ]
            },
            'database': {
                'type': 'SQL_Server',
                'entities': [
                    {
                        'name': 'User',
                        'properties': [
                            {'name': 'Id', 'type': 'int', 'key': True},
                            {'name': 'Password', 'type': 'string'}  # Problema de segurança
                        ]
                    }
                ]
            }
        }
        
        # Cria projeto
        result = await self.system.create_project(project_config)
        
        # Executa validação
        validation = await self.system.validate_project(result['project_id'])
        
        # Verifica problemas encontrados
        self.assertFalse(validation['passed'])
        self.assertTrue(len(validation['issues']) > 0)
        
        # Verifica tipos específicos de problemas
        issue_types = [issue['type'] for issue in validation['issues']]
        self.assertIn('security_vulnerability', issue_types)
        self.assertIn('best_practice_violation', issue_types)
        
        # Verifica recomendações
        self.assertTrue(len(validation['recommendations']) > 0)
        recs = validation['recommendations']
        self.assertTrue(any('password hash' in r.lower() for r in recs))

    async def test_project_analysis(self):
        """Testa análise de projeto"""
        # Cria projeto para análise
        project_config = {
            'name': 'AnalysisTest',
            'type': 'WPF',
            'features': ['user_authentication', 'data_persistence']
        }
        
        result = await self.system.create_project(project_config)
        
        # Executa análise
        analysis = await self.system.analyze_project(result['project_id'])
        
        # Verifica métricas
        self.assertIn('metrics', analysis)
        metrics = analysis['metrics']
        self.assertIn('code_quality', metrics)
        self.assertIn('performance', metrics)
        self.assertIn('security', metrics)
        
        # Verifica análise de dependências
        self.assertIn('dependencies', analysis)
        deps = analysis['dependencies']
        self.assertTrue(len(deps['direct']) > 0)
        self.assertTrue(len(deps['indirect']) > 0)
        
        # Verifica análise de complexidade
        self.assertIn('complexity', analysis)
        complexity = analysis['complexity']
        self.assertIn('cyclomatic', complexity)
        self.assertIn('cognitive', complexity)
        
        # Verifica sugestões
        self.assertIn('suggestions', analysis)
        self.assertTrue(len(analysis['suggestions']) > 0)

if __name__ == '__main__':
    unittest.main()