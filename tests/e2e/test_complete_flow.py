# tests/e2e/test_complete_flow.py

import unittest
import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch

from kallista.agents import (
    ArchitectAgent,
    WPFAgent,
    DatabaseAgent,
    SecurityAgent
)
from kallista.tools.wpf import ComponentGenerator
from kallista.workflows import WPFProjectWorkflow
from kallista.integrations.visual_studio import VSIntegration
from kallista.core.management import StateManager, ContextManager
from kallista.tools.testing import TestRunner
from kallista.tools.security import SecurityScanner
from kallista.integrations.nuget import PackageManager

class TestCompleteProjectFlow(unittest.TestCase):
    """End-to-end tests for complete project workflows."""

    async def asyncSetUp(self):
        """Setup test environment."""
        # Initialize core managers
        self.state_manager = StateManager()
        self.context_manager = ContextManager()
        await self.state_manager.initialize()
        await self.context_manager.initialize()
        
        # Initialize agents
        self.architect_agent = ArchitectAgent()
        self.wpf_agent = WPFAgent()
        self.db_agent = DatabaseAgent()
        self.security_agent = SecurityAgent()
        
        # Initialize tools
        self.component_generator = ComponentGenerator()
        self.test_runner = TestRunner()
        self.security_scanner = SecurityScanner()
        
        # Initialize integrations
        self.vs_integration = VSIntegration()
        self.package_manager = PackageManager()
        
        # Initialize workflow
        self.project_workflow = WPFProjectWorkflow()
        
        # Setup test project configuration
        self.test_project_config = {
            'name': 'TestE2EProject',
            'type': 'WPF',
            'template': 'mvvm-basic',
            'features': ['authentication', 'database', 'logging'],
            'settings': {
                'target_framework': 'net6.0-windows',
                'use_entity_framework': True,
                'database_type': 'SQLite',
                'authentication_type': 'local',
                'logging_level': 'Debug'
            }
        }
        
        # Create test directory
        self.test_dir = Path('./TestE2EProject')
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()

    async def asyncTearDown(self):
        """Cleanup test environment."""
        await self.state_manager.cleanup()
        await self.context_manager.cleanup()
        
        # Cleanup test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    async def test_001_complete_project_creation(self):
        """Test complete project creation flow from architecture to deployment."""
        # 1. System Design Phase
        design = await self.architect_agent.design_system(self.test_project_config)
        self.assertIsNotNone(design)
        self.assertIn('architecture', design)
        self.assertIn('components', design)
        
        # Validate design
        validation_result = await self.architect_agent.validate_design(design)
        self.assertTrue(validation_result['is_valid'])
        self.assertEqual(len(validation_result['issues']), 0)

        # 2. Project Setup Phase
        workflow_result = await self.project_workflow.execute(self.test_project_config)
        self.assertTrue(workflow_result['success'])
        self.assertTrue(self.test_dir.exists())
        
        # Verify project structure
        required_files = [
            'TestE2EProject.sln',
            'TestE2EProject.csproj',
            'App.xaml',
            'MainWindow.xaml',
            'App.config'
        ]
        for file in required_files:
            self.assertTrue((self.test_dir / file).exists())

        # 3. UI Component Generation
        ui_components = [
            {
                'name': 'MainDashboard',
                'type': 'View',
                'features': ['data-grid', 'filtering', 'sorting']
            },
            {
                'name': 'UserManagement',
                'type': 'View',
                'features': ['crud', 'validation', 'search']
            }
        ]
        
        for component in ui_components:
            ui_result = await self.wpf_agent.design_interface(component)
            self.assertTrue(ui_result['success'])
            self.assertIn('xaml_code', ui_result)
            self.assertIn('cs_code', ui_result)
            
            # Generate and verify component files
            await self.component_generator.generate(
                self.test_dir,
                component,
                ui_result
            )
            
            view_file = self.test_dir / f"Views/{component['name']}View.xaml"
            viewmodel_file = self.test_dir / f"ViewModels/{component['name']}ViewModel.cs"
            self.assertTrue(view_file.exists())
            self.assertTrue(viewmodel_file.exists())

        # 4. Database Setup
        db_config = {
            'name': 'TestE2EProjectDB',
            'type': 'SQLite',
            'models': [
                {
                    'name': 'User',
                    'properties': [
                        {'name': 'Id', 'type': 'int', 'key': 'primary'},
                        {'name': 'Username', 'type': 'string'},
                        {'name': 'Email', 'type': 'string'}
                    ]
                },
                {
                    'name': 'Product',
                    'properties': [
                        {'name': 'Id', 'type': 'int', 'key': 'primary'},
                        {'name': 'Name', 'type': 'string'},
                        {'name': 'Price', 'type': 'decimal'}
                    ]
                }
            ]
        }
        
        db_result = await self.db_agent.setup_database(db_config)
        self.assertTrue(db_result['success'])
        self.assertIn('connection_string', db_result)
        self.assertIn('migrations', db_result)
        
        # Verify database files
        db_file = self.test_dir / 'Data/TestE2EProjectDB.db'
        context_file = self.test_dir / 'Data/ApplicationDbContext.cs'
        self.assertTrue(db_file.exists())
        self.assertTrue(context_file.exists())

        # 5. Security Implementation
        security_result = await self.security_agent.implement_security({
            'authentication': True,
            'authorization': True,
            'data_protection': True
        })
        self.assertTrue(security_result['success'])
        
        # Verify security implementation
        security_files = [
            'Security/AuthenticationService.cs',
            'Security/AuthorizationHandler.cs',
            'Security/DataProtector.cs'
        ]
        for file in security_files:
            self.assertTrue((self.test_dir / file).exists())

        # 6. Test Setup and Execution
        test_setup_result = await self.vs_integration.setup_tests(
            project_path=self.test_dir,
            test_framework="xUnit",
            test_categories=["Unit", "Integration"]
        )
        self.assertTrue(test_setup_result['success'])
        
        # Run tests
        test_result = await self.test_runner.run_tests(
            project_path=self.test_dir,
            categories=["Unit", "Integration"]
        )
        self.assertTrue(test_result['success'])
        self.assertGreater(test_result['total_tests'], 0)
        self.assertEqual(test_result['failed_tests'], 0)

        # 7. Security Scan
        scan_result = await self.security_scanner.scan_project(
            project_path=self.test_dir,
            scan_dependencies=True,
            scan_code=True
        )
        self.assertTrue(scan_result['success'])
        self.assertEqual(len(scan_result['critical_issues']), 0)

        # 8. Package Management
        package_result = await self.package_manager.prepare_package(
            project_path=self.test_dir,
            version="1.0.0",
            generate_documentation=True
        )
        self.assertTrue(package_result['success'])
        self.assertTrue((self.test_dir / 'bin/Release/TestE2EProject.1.0.0.nupkg').exists())

def run_async_test(coro):
    """Helper to run async tests."""
    return asyncio.get_event_loop().run_until_complete(coro)

if __name__ == '__main__':
    unittest.main()