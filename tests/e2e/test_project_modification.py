# tests/e2e/test_project_modification.py

import unittest
import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any

from kallista.agents import (
    WPFAgent,
    DatabaseAgent,
    ApiAgent,
    SecurityAgent
)
from kallista.tools.wpf import ComponentGenerator, TemplateGenerator
from kallista.tools.database import SchemaGenerator
from kallista.tools.api import ServiceGenerator
from kallista.integrations.visual_studio import VSIntegration
from kallista.core.management import StateManager, ContextManager
from kallista.tools.testing import TestRunner
from kallista.tools.code import Analyzer

class TestProjectModification(unittest.TestCase):
    """End-to-end tests for project modification scenarios."""

    async def asyncSetUp(self):
        """Setup test environment with existing project."""
        # Initialize managers
        self.state_manager = StateManager()
        self.context_manager = ContextManager()
        await self.state_manager.initialize()
        await self.context_manager.initialize()
        
        # Initialize agents
        self.wpf_agent = WPFAgent()
        self.db_agent = DatabaseAgent()
        self.api_agent = ApiAgent()
        self.security_agent = SecurityAgent()
        
        # Initialize tools
        self.component_generator = ComponentGenerator()
        self.template_generator = TemplateGenerator()
        self.schema_generator = SchemaGenerator()
        self.service_generator = ServiceGenerator()
        self.test_runner = TestRunner()
        self.code_analyzer = Analyzer()
        
        # Initialize integrations
        self.vs_integration = VSIntegration()
        
        # Setup test project path
        self.test_dir = Path('./TestModificationProject')
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            
        # Create basic project structure
        await self._create_base_project()

    async def _create_base_project(self):
        """Creates a base project for modification tests."""
        base_config = {
            'name': 'TestModificationProject',
            'type': 'WPF',
            'template': 'mvvm-basic',
            'features': ['basic-auth', 'sqlite-db']
        }
        
        self.wpf_agent.create_project(base_config)
        
        # Create initial structure
        initial_files = [
            'App.xaml',
            'MainWindow.xaml',
            'Views/LoginView.xaml',
            'ViewModels/LoginViewModel.cs',
            'Models/User.cs',
            'Services/AuthService.cs'
        ]
        
        for file in initial_files:
            file_path = self.test_dir / file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()

    async def asyncTearDown(self):
        """Cleanup test environment."""
        await self.state_manager.cleanup()
        await self.context_manager.cleanup()
        
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    async def test_001_add_new_feature(self):
        """Test adding a new feature to existing project."""
        # 1. Update existing login view
        update_config = {
            'component': 'LoginView',
            'changes': {
                'add_features': ['remember-me', 'password-reset', 'oauth'],
                'modify_layout': {
                    'type': 'material',
                    'theme': 'modern',
                    'responsiveness': True
                },
                'add_validations': [
                    {'field': 'username', 'rules': ['required', 'email']},
                    {'field': 'password', 'rules': ['required', 'min-length:8']}
                ]
            }
        }
        
        # Apply updates
        result = await self.wpf_agent.update_component(update_config)
        self.assertTrue(result['success'])
        
        # Verify updates
        login_view_path = self.test_dir / 'Views/LoginView.xaml'
        login_vm_path = self.test_dir / 'ViewModels/LoginViewModel.cs'
        
        # Check XAML changes
        xaml_content = login_view_path.read_text()
        self.assertIn('MaterialDesign', xaml_content)
        self.assertIn('RememberMe', xaml_content)
        self.assertIn('PasswordReset', xaml_content)
        self.assertIn('OAuthLogin', xaml_content)
        
        # Check ViewModel changes
        vm_content = login_vm_path.read_text()
        self.assertIn('RememberMeProperty', vm_content)
        self.assertIn('PasswordResetCommand', vm_content)
        self.assertIn('OAuthLoginCommand', vm_content)
        self.assertIn('IDataValidator', vm_content)

    async def test_003_add_api_integration(self):
        """Test adding API integration to existing project."""
        # 1. Configure API integration
        api_config = {
            'type': 'REST',
            'base_url': 'https://api.example.com',
            'endpoints': [
                {
                    'name': 'Users',
                    'operations': ['GET', 'POST', 'PUT', 'DELETE'],
                    'auth_required': True
                },
                {
                    'name': 'Products',
                    'operations': ['GET', 'POST'],
                    'auth_required': True
                }
            ],
            'authentication': {
                'type': 'JWT',
                'refresh_token': True
            },
            'features': [
                'retry-policy',
                'caching',
                'logging'
            ]
        }
        
        # Generate API integration
        result = await self.api_agent.integrate_api(api_config)
        self.assertTrue(result['success'])
        
        # Verify API client generation
        expected_files = [
            'Services/Api/ApiClient.cs',
            'Services/Api/UserApiService.cs',
            'Services/Api/ProductApiService.cs',
            'Models/Api/ApiModels.cs',
            'Config/ApiConfig.json'
        ]
        
        for file in expected_files:
            self.assertTrue((self.test_dir / file).exists())
        
        # Verify integration tests
        test_result = await self.test_runner.run_tests(
            project_path=self.test_dir,
            test_pattern="*Api*.cs"
        )
        self.assertTrue(test_result['success'])

    async def test_004_add_database_migration(self):
        """Test adding new database migration."""
        # 1. Add new entity
        new_entity = {
            'name': 'Order',
            'properties': [
                {'name': 'Id', 'type': 'int', 'key': 'primary'},
                {'name': 'UserId', 'type': 'int', 'foreign_key': 'User'},
                {'name': 'OrderDate', 'type': 'DateTime'},
                {'name': 'Status', 'type': 'string'},
                {'name': 'TotalAmount', 'type': 'decimal'}
            ],
            'relationships': [
                {
                    'type': 'many-to-one',
                    'entity': 'User',
                    'foreign_key': 'UserId'
                }
            ]
        }
        
        # Generate migration
        result = await self.db_agent.add_entity(new_entity)
        self.assertTrue(result['success'])
        
        # Verify migration files
        migration_path = self.test_dir / 'Data/Migrations'
        migrations = list(migration_path.glob('*_AddOrderEntity.cs'))
        self.assertEqual(len(migrations), 1)
        
        # Verify entity file
        order_model_path = self.test_dir / 'Models/Order.cs'
        self.assertTrue(order_model_path.exists())
        
        # Verify DbContext update
        context_path = self.test_dir / 'Data/ApplicationDbContext.cs'
        context_content = context_path.read_text()
        self.assertIn('DbSet<Order>', context_content)
        self.assertIn('modelBuilder.Entity<Order>', context_content)
        
        # Run database tests
        test_result = await self.test_runner.run_tests(
            project_path=self.test_dir,
            test_pattern="*Order*.cs"
        )
        self.assertTrue(test_result['success'])

    async def test_005_update_project_structure(self):
        """Test updating project structure and organization."""
        # 1. Configure new project structure
        structure_update = {
            'modules': [
                {
                    'name': 'Core',
                    'folders': ['Common', 'Interfaces', 'Extensions']
                },
                {
                    'name': 'Features',
                    'folders': ['Auth', 'Users', 'Reports', 'Orders']
                },
                {
                    'name': 'Infrastructure',
                    'folders': ['Data', 'Services', 'Security']
                }
            ],
            'move_rules': [
                {'pattern': '*View.xaml', 'target': 'Features/{module}'},
                {'pattern': '*Service.cs', 'target': 'Infrastructure/Services'},
                {'pattern': '*Model.cs', 'target': 'Core/Common'}
            ]
        }
        
        # Apply structure update
        result = await self.wpf_agent.update_project_structure(structure_update)
        self.assertTrue(result['success'])
        
        # Verify new structure
        for module in structure_update['modules']:
            module_path = self.test_dir / module['name']
            self.assertTrue(module_path.exists())
            for folder in module['folders']:
                self.assertTrue((module_path / folder).exists())
        
        # Verify file movements
        self.assertTrue((self.test_dir / 'Features/Auth/LoginView.xaml').exists())
        self.assertTrue((self.test_dir / 'Infrastructure/Services/AuthService.cs').exists())
        self.assertTrue((self.test_dir / 'Core/Common/UserModel.cs').exists())
        
        # Run all tests after restructure
        test_result = await self.test_runner.run_tests(
            project_path=self.test_dir
        )
        self.assertTrue(test_result['success'])
        
        # Verify build after restructure
        build_result = await self.vs_integration.build_project(self.test_dir)
        self.assertTrue(build_result['success'])

def run_async_test(coro):
    """Helper to run async tests."""
    return asyncio.get_event_loop().run_until_complete(coro)

    async def test_006_add_localization(self):
        """Test adding localization support to the project."""
        # 1. Configure localization
        localization_config = {
            'default_language': 'pt-BR',
            'supported_languages': ['en-US', 'pt-BR', 'es-ES'],
            'resource_location': 'Resources/Strings',
            'auto_generate': True
        }

        # Add localization support
        result = await self.wpf_agent.add_localization(localization_config)
        self.assertTrue(result['success'])

        # Verify resource files
        for lang in localization_config['supported_languages']:
            resource_file = self.test_dir / f"Resources/Strings/Messages.{lang}.resx"
            self.assertTrue(resource_file.exists())

        # Verify localization implementation
        expected_files = [
            'Services/LocalizationService.cs',
            'Config/LocalizationConfig.json',
            'Extensions/LocalizationExtensions.cs'
        ]
        for file in expected_files:
            self.assertTrue((self.test_dir / file).exists())

    async def test_007_theme_customization(self):
        """Test adding and customizing themes."""
        # 1. Configure theme system
        theme_config = {
            'base_theme': 'Material',
            'color_schemes': [
                {
                    'name': 'Light',
                    'primary': '#1976D2',
                    'secondary': '#424242',
                    'accent': '#82B1FF'
                },
                {
                    'name': 'Dark',
                    'primary': '#333333',
                    'secondary': '#424242',
                    'accent': '#82B1FF'
                }
            ],
            'custom_controls': True
        }

        # Implement theme system
        result = await self.wpf_agent.implement_theming(theme_config)
        self.assertTrue(result['success'])

        # Verify theme files
        expected_files = [
            'Themes/Light.xaml',
            'Themes/Dark.xaml',
            'Themes/CustomControls.xaml',
            'Services/ThemeService.cs'
        ]
        for file in expected_files:
            self.assertTrue((self.test_dir / file).exists())

    async def test_008_add_logging_system(self):
        """Test adding comprehensive logging system."""
        # 1. Configure logging
        logging_config = {
            'providers': ['file', 'console', 'azure'],
            'levels': ['debug', 'info', 'warning', 'error'],
            'features': {
                'structured_logging': True,
                'performance_logging': True,
                'audit_logging': True
            }
        }

        # Implement logging
        result = await self.wpf_agent.add_logging(logging_config)
        self.assertTrue(result['success'])

        # Verify logging implementation
        expected_files = [
            'Services/Logging/LoggingService.cs',
            'Services/Logging/FileLogger.cs',
            'Services/Logging/AzureLogger.cs',
            'Config/logging.json'
        ]
        for file in expected_files:
            self.assertTrue((self.test_dir / file).exists())

    async def test_009_dependency_injection_setup(self):
        """Test setting up dependency injection."""
        # 1. Configure DI
        di_config = {
            'container': 'Microsoft.Extensions.DependencyInjection',
            'lifetime_scopes': ['singleton', 'scoped', 'transient'],
            'auto_registration': True
        }

        # Implement DI
        result = await self.wpf_agent.setup_dependency_injection(di_config)
        self.assertTrue(result['success'])

        # Verify DI setup
        expected_files = [
            'Config/ServiceConfiguration.cs',
            'Extensions/ServiceCollectionExtensions.cs',
            'App.xaml.cs'  # Should be modified to include DI configuration
        ]
        for file in expected_files:
            self.assertTrue((self.test_dir / file).exists())

        # Verify App.xaml.cs modifications
        app_content = (self.test_dir / 'App.xaml.cs').read_text()
        self.assertIn('IServiceProvider', app_content)
        self.assertIn('ConfigureServices', app_content)

    async def test_010_add_state_management(self):
        """Test adding state management system."""
        # 1. Configure state management
        state_config = {
            'type': 'redux',
            'features': {
                'time_travel': True,
                'persistence': True,
                'dev_tools': True
            },
            'stores': ['auth', 'data', 'ui']
        }

        # Implement state management
        result = await self.wpf_agent.add_state_management(state_config)
        self.assertTrue(result['success'])

        # Verify state management implementation
        expected_files = [
            'State/Store.cs',
            'State/Reducers',
            'State/Actions',
            'State/Middleware',
            'Extensions/StateExtensions.cs'
        ]
        for file in expected_files:
            self.assertTrue((self.test_dir / file).exists())

def run_async_test(coro):
    """Helper to run async tests."""
    return asyncio.get_event_loop().run_until_complete(coro)

if __name__ == '__main__':
    unittest.main() Add Report Generation Feature
        feature_config = {
            'name': 'ReportGenerator',
            'type': 'Feature',
            'components': [
                {
                    'name': 'ReportDesigner',
                    'type': 'View',
                    'features': ['drag-drop', 'preview', 'export']
                },
                {
                    'name': 'ReportTemplate',
                    'type': 'View',
                    'features': ['customization', 'save-load']
                }
            ],
            'services': [
                {
                    'name': 'ReportService',
                    'operations': ['generate', 'export', 'template-management']
                }
            ],
            'models': [
                {
                    'name': 'Report',
                    'properties': [
                        {'name': 'Id', 'type': 'int'},
                        {'name': 'Name', 'type': 'string'},
                        {'name': 'Template', 'type': 'string'},
                        {'name': 'Created', 'type': 'DateTime'}
                    ]
                }
            ]
        }
        
        # Generate feature components
        result = await self.wpf_agent.add_feature(feature_config)
        self.assertTrue(result['success'])
        
        # Verify component creation
        for component in feature_config['components']:
            view_path = self.test_dir / f"Views/{component['name']}View.xaml"
            viewmodel_path = self.test_dir / f"ViewModels/{component['name']}ViewModel.cs"
            self.assertTrue(view_path.exists())
            self.assertTrue(viewmodel_path.exists())
        
        # Verify service creation
        for service in feature_config['services']:
            service_path = self.test_dir / f"Services/{service['name']}.cs"
            self.assertTrue(service_path.exists())
        
        # Verify model creation
        for model in feature_config['models']:
            model_path = self.test_dir / f"Models/{model['name']}.cs"
            self.assertTrue(model_path.exists())
        
        # Run tests for new feature
        test_result = await self.test_runner.run_tests(
            project_path=self.test_dir,
            test_pattern=f"*Report*.cs"
        )
        self.assertTrue(test_result['success'])
        self.assertEqual(test_result['failed_tests'], 0)

    async def test_002_update_existing_component(self):
        """Test updating an existing component."""
        # 1.