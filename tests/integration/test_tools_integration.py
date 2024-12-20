# tests/integration/test_tools_integration.py
import unittest
import asyncio
from pathlib import Path
import json
from datetime import datetime

from tools.code.generator import CodeGenerator
from tools.code.analyzer import CodeAnalyzer
from tools.wpf.xaml_generator import XamlGenerator
from tools.wpf.style_generator import StyleGenerator
from tools.database.schema_generator import SchemaGenerator
from tools.security.security_scanner import SecurityScanner
from tools.testing.test_runner import TestRunner

class TestToolsIntegration(unittest.TestCase):
    def setUp(self):
        """Setup para os testes de integração de ferramentas"""
        # Configurações
        self.config = {
            'output_dir': 'test_output',
            'templates_dir': 'test_templates',
            'scan_rules': 'test_rules.json'
        }
        
        # Cria diretórios de teste
        Path(self.config['output_dir']).mkdir(exist_ok=True)
        Path(self.config['templates_dir']).mkdir(exist_ok=True)
        
        # Inicializa ferramentas
        self.code_generator = CodeGenerator(self.config)
        self.code_analyzer = CodeAnalyzer(self.config)
        self.xaml_generator = XamlGenerator(self.config)
        self.style_generator = StyleGenerator(self.config)
        self.schema_generator = SchemaGenerator(self.config)
        self.security_scanner = SecurityScanner(self.config)
        self.test_runner = TestRunner(self.config)

    def tearDown(self):
        """Limpeza após os testes"""
        # Remove diretórios e arquivos de teste
        import shutil
        shutil.rmtree(self.config['output_dir'], ignore_errors=True)
        shutil.rmtree(self.config['templates_dir'], ignore_errors=True)
        
        if Path('test_rules.json').exists():
            Path('test_rules.json').unlink()

    async def test_code_generation_workflow(self):
        """Testa workflow de geração de código"""
        # Configuração do projeto
        project_config = {
            'name': 'TestProject',
            'type': 'WPF',
            'components': [
                {
                    'name': 'UserManagement',
                    'type': 'Module',
                    'features': ['crud', 'authentication']
                }
            ]
        }
        
        # 1. Gera código
        generated = await self.code_generator.generate_project(project_config)
        
        # 2. Analisa código gerado
        analysis = await self.code_analyzer.analyze_code(
            generated['output_dir']
        )
        
        # 3. Executa testes
        test_results = await self.test_runner.run_tests(
            generated['output_dir']
        )
        
        # Verifica resultados
        self.assertTrue(generated['success'])
        self.assertIsNotNone(analysis['metrics'])
        self.assertTrue(test_results['success'])
        
        # Verifica estrutura gerada
        project_dir = Path(generated['output_dir'])
        self.assertTrue((project_dir / 'UserManagement').exists())
        self.assertTrue(
            (project_dir / 'UserManagement/ViewModels').exists()
        )
        self.assertTrue(
            (project_dir / 'UserManagement/Models').exists()
        )

    async def test_ui_generation_workflow(self):
        """Testa workflow de geração de UI"""
        # Configuração da UI
        ui_config = {
            'component': 'UserDashboard',
            'type': 'Page',
            'layout': 'grid',
            'elements': [
                {
                    'type': 'DataGrid',
                    'name': 'UsersGrid',
                    'binding': 'Users'
                },
                {
                    'type': 'Button',
                    'name': 'AddUser',
                    'content': 'Add User'
                }
            ]
        }
        
        # 1. Gera XAML
        xaml = await self.xaml_generator.generate_xaml(ui_config)
        
        # 2. Gera estilos
        styles = await self.style_generator.generate_styles(ui_config)
        
        # 3. Analisa XAML gerado
        analysis = await self.code_analyzer.analyze_xaml(xaml)
        
        # Verifica resultados
        self.assertIsNotNone(xaml)
        self.assertTrue(xaml.startswith('<UserControl'))
        self.assertIn('UsersGrid', xaml)
        self.assertIn('AddUser', xaml)
        
        self.assertIsNotNone(styles)
        self.assertTrue(styles.startswith('<ResourceDictionary'))
        
        self.assertTrue(analysis['valid'])
        self.assertEqual(analysis['elements_count'], 2)

    async def test_database_schema_workflow(self):
        """Testa workflow de geração de schema de banco de dados"""
        # Configuração do schema
        schema_config = {
            'entities': [
                {
                    'name': 'User',
                    'properties': [
                        {'name': 'Id', 'type': 'int', 'key': True},
                        {'name': 'Username', 'type': 'string'},
                        {'name': 'Email', 'type': 'string'}
                    ]
                },
                {
                    'name': 'Role',
                    'properties': [
                        {'name': 'Id', 'type': 'int', 'key': True},
                        {'name': 'Name', 'type': 'string'}
                    ]
                }
            ],
            'relationships': [
                {
                    'from': 'User',
                    'to': 'Role',
                    'type': 'many-to-many'
                }
            ]
        }
        
        # 1. Gera schema
        schema = await self.schema_generator.generate_schema(schema_config)
        
        # 2. Analisa schema
        analysis = await self.schema_generator.analyze_schema(schema)
        
        # 3. Gera código Entity Framework
        ef_code = await self.schema_generator.generate_ef_code(schema)
        
        # Verifica resultados
        self.assertTrue(schema['valid'])
        self.assertEqual(len(schema['entities']), 2)
        self.assertEqual(len(schema['relationships']), 1)
        
        self.assertTrue(analysis['valid'])
        self.assertFalse(analysis['circular_dependencies'])
        
        self.assertIn('DbContext', ef_code)
        self.assertIn('public class User', ef_code)
        self.assertIn('public class Role', ef_code)

    async def test_security_analysis_workflow(self):
        """Testa workflow de análise de segurança"""
        # Gera código de teste com vulnerabilidades conhecidas
        test_code = '''
            public class UserController {
                public async Task<IActionResult> Login(string username, string password) {
                    var query = $"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{password}'";
                    // SQL Injection vulnerability
                    
                    var apiKey = "sk_test_123456";  // Hard-coded credential
                    # tests/integration/test_tools_integration.py (continuação)
                    return Json(new { success = true });
                }
                
                public void ProcessData(string input) {
                    eval(input);  // Code injection vulnerability
                }
            }
        '''
        
        test_file = Path(self.config['output_dir']) / 'test_code.cs'
        test_file.write_text(test_code)
        
        # 1. Executa scan de segurança
        scan_results = await self.security_scanner.scan_code(test_file)
        
        # 2. Analisa resultados
        analysis = await self.security_scanner.analyze_results(scan_results)
        
        # 3. Gera relatório
        report = await self.security_scanner.generate_report(analysis)
        
        # Verifica resultados
        self.assertTrue(len(scan_results['vulnerabilities']) > 0)
        
        # Verifica tipos específicos de vulnerabilidades
        vuln_types = [v['type'] for v in scan_results['vulnerabilities']]
        self.assertIn('sql_injection', vuln_types)
        self.assertIn('hardcoded_credential', vuln_types)
        self.assertIn('code_injection', vuln_types)
        
        # Verifica análise
        self.assertGreater(analysis['risk_score'], 7.0)  # Alto risco
        self.assertTrue(analysis['requires_immediate_action'])
        
        # Verifica relatório
        self.assertIn('SQL Injection', report['high_priority'])
        self.assertIn('recommendations', report)

    async def test_test_generation_workflow(self):
        """Testa workflow de geração de testes"""
        # Código para testar
        test_class = '''
            public class Calculator {
                public int Add(int a, int b) {
                    return a + b;
                }
                
                public int Divide(int a, int b) {
                    if (b == 0) throw new DivideByZeroException();
                    return a / b;
                }
            }
        '''
        
        test_file = Path(self.config['output_dir']) / 'Calculator.cs'
        test_file.write_text(test_class)
        
        # 1. Gera testes unitários
        generated_tests = await self.test_runner.generate_tests(test_file)
        
        # 2. Executa testes gerados
        test_results = await self.test_runner.run_tests(
            generated_tests['output_dir']
        )
        
        # 3. Analisa cobertura
        coverage = await self.test_runner.analyze_coverage(test_results)
        
        # Verifica testes gerados
        self.assertTrue(generated_tests['success'])
        self.assertTrue(len(generated_tests['test_files']) > 0)
        
        # Verifica métodos testados
        test_methods = generated_tests['test_methods']
        self.assertIn('TestAdd', test_methods)
        self.assertIn('TestDivide', test_methods)
        self.assertIn('TestDivideByZero', test_methods)
        
        # Verifica execução dos testes
        self.assertTrue(test_results['success'])
        self.assertEqual(test_results['failed'], 0)
        
        # Verifica cobertura
        self.assertGreater(coverage['line_coverage'], 90)
        self.assertGreater(coverage['branch_coverage'], 90)

    async def test_tool_chain_integration(self):
        """Testa integração completa da cadeia de ferramentas"""
        # Configuração do projeto
        project_config = {
            'name': 'IntegrationTest',
            'type': 'WPF',
            'modules': [
                {
                    'name': 'Users',
                    'type': 'Module',
                    'entities': [
                        {
                            'name': 'User',
                            'properties': [
                                {'name': 'Id', 'type': 'int'},
                                {'name': 'Name', 'type': 'string'}
                            ]
                        }
                    ],
                    'ui': {
                        'views': [
                            {
                                'name': 'UserList',
                                'type': 'Page',
                                'elements': [
                                    {'type': 'DataGrid', 'binding': 'Users'}
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        # 1. Gera código e UI
        generated_code = await self.code_generator.generate_project(project_config)
        generated_xaml = await self.xaml_generator.generate_module_xaml(
            project_config['modules'][0]
        )
        
        # 2. Gera schema de banco de dados
        schema = await self.schema_generator.generate_schema_from_entities(
            project_config['modules'][0]['entities']
        )
        
        # 3. Analisa código e segurança
        code_analysis = await self.code_analyzer.analyze_code(
            generated_code['output_dir']
        )
        security_scan = await self.security_scanner.scan_code(
            generated_code['output_dir']
        )
        
        # 4. Gera e executa testes
        generated_tests = await self.test_runner.generate_tests(
            generated_code['output_dir']
        )
        test_results = await self.test_runner.run_tests(
            generated_tests['output_dir']
        )
        
        # Verifica integração completa
        self.assertTrue(generated_code['success'])
        self.assertIsNotNone(generated_xaml)
        self.assertTrue(schema['valid'])
        
        # Verifica análises
        self.assertTrue(code_analysis['valid'])
        self.assertEqual(len(security_scan['vulnerabilities']), 0)
        
        # Verifica testes
        self.assertTrue(test_results['success'])
        self.assertEqual(test_results['failed'], 0)
        
        # Verifica estrutura do projeto
        project_dir = Path(generated_code['output_dir'])
        self.assertTrue((project_dir / 'Users').exists())
        self.assertTrue((project_dir / 'Users/Views').exists())
        self.assertTrue((project_dir / 'Users/ViewModels').exists())
        self.assertTrue((project_dir / 'Users/Models').exists())
        
        # Verifica arquivos gerados
        self.assertTrue((project_dir / 'Users/Views/UserList.xaml').exists())
        self.assertTrue((project_dir / 'Users/Models/User.cs').exists())
        self.assertTrue((project_dir / 'Users/ViewModels/UserListViewModel.cs').exists())

if __name__ == '__main__':
    unittest.main()
                   