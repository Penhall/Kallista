# tests/security/test_compliance_checker.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
from datetime import datetime

from tools.security.compliance_checker import ComplianceChecker

class TestComplianceChecker(unittest.TestCase):
    def setUp(self):
        self.checker = ComplianceChecker()
        self.test_path = Path("test_project")
        self.test_files = {
            'TestController.cs': '''
                public class TestController : Controller {
                    [HttpPost]
                    public ActionResult ProcessData(string input) {
                        var data = input;  // Sem validação
                        var query = $"SELECT * FROM Users WHERE id = {input}";  // SQL Injection
                        return Json(data);
                    }

                    public ActionResult GetUserData(int id) {
                        var user = _context.Users.Find(id);
                        return Json(user);  // Exposição de dados sensíveis
                    }
                }
            ''',
            'User.cs': '''
                public class User {
                    public int Id { get; set; }
                    public string Email { get; set; }
                    public string Password { get; set; }  // Dados sensíveis
                    public string SocialSecurityNumber { get; set; }  // GDPR
                }
            ''',
            'Web.config': '''
                <?xml version="1.0"?>
                <configuration>
                    <system.web>
                        <compilation debug="true" />
                        <trace enabled="true" />
                        <customErrors mode="Off" />
                    </system.web>
                </configuration>
            '''
        }

    async def asyncSetUp(self):
        # Setup assíncrono
        self.test_path.mkdir(exist_ok=True)
        for filename, content in self.test_files.items():
            (self.test_path / filename).write_text(content)

    def tearDown(self):
        # Limpa arquivos de teste
        if self.test_path.exists():
            import shutil
            shutil.rmtree(self.test_path)

    def test_init(self):
        """Testa inicialização do checker"""
        self.assertIsNotNone(self.checker)
        self.assertIsNotNone(self.checker.rules)
        self.assertIn('owasp', self.checker.rules)
        self.assertIn('gdpr', self.checker.rules)
        self.assertIn('security_best_practices', self.checker.rules)

    async def test_check_compliance(self):
        """Testa verificação completa de compliance"""
        await self.asyncSetUp()
        
        results = await self.checker.check_compliance(self.test_path)
        
        # Verifica estrutura do resultado
        self.assertIn('owasp_compliance', results)
        self.assertIn('gdpr_compliance', results)
        self.assertIn('best_practices', results)
        self.assertIn('total_issues', results)
        self.assertIn('compliance_score', results)
        self.assertIn('timestamp', results)
        
        # Verifica se encontrou issues
        self.assertTrue(results['total_issues'] > 0)
        self.assertTrue(len(results['owasp_compliance']) > 0)
        self.assertTrue(len(results['gdpr_compliance']) > 0)
        self.assertTrue(len(results['best_practices']) > 0)

    async def test_check_owasp_compliance(self):
        """Testa verificação de compliance OWASP"""
        await self.asyncSetUp()
        
        results = await self.checker._check_owasp_compliance(self.test_path)
        
        # Verifica SQL Injection
        sql_issue = next(
            (r for r in results if r['category'] == 'Injection'),
            None
        )
        self.assertIsNotNone(sql_issue)
        self.assertEqual(sql_issue['severity'], 'high')
        
        # Verifica exposição de dados sensíveis
        exposure_issue = next(
            (r for r in results 
             if r['category'] == 'Sensitive Data Exposure'),
            None
        )
        self.assertIsNotNone(exposure_issue)
        self.assertEqual(exposure_issue['severity'], 'high')

    async def test_check_gdpr_compliance(self):
        """Testa verificação de compliance GDPR"""
        await self.asyncSetUp()
        
        results = await self.checker._check_gdpr_compliance(self.test_path)
        
        # Verifica processamento de dados pessoais
        personal_data_issue = next(
            (r for r in results 
             if r['category'] == 'Personal Data'),
            None
        )
        self.assertIsNotNone(personal_data_issue)
        self.assertEqual(personal_data_issue['severity'], 'high')
        
        # Verifica proteção de dados
        protection_issue = next(
            (r for r in results 
             if r['category'] == 'Data Protection'),
            None
        )
        self.assertIsNotNone(protection_issue)

    async def test_check_security_best_practices(self):
        """Testa verificação de melhores práticas"""
        await self.asyncSetUp()
        
        results = await self.checker._check_security_best_practices(self.test_path)
        
        # Verifica validação de entrada
        validation_issue = next(
            (r for r in results 
             if r['category'] == 'Input Validation'),
            None
        )
        self.assertIsNotNone(validation_issue)
        
        # Verifica configuração segura
        config_issue = next(
            (r for r in results 
             if r['category'] == 'Secure Configuration'),
            None
        )
        self.assertIsNotNone(config_issue)

# tests/security/test_compliance_checker.py (continuação)
    async def test_check_rule(self):
        """Testa verificação de regra específica"""
        await self.asyncSetUp()
        
        rule = {
            'id': 'TEST-001',
            'category': 'Test',
            'severity': 'high',
            'description': 'Test rule',
            'patterns': [r'password\s*=\s*["\'].*["\']'],
            'file_types': ['.cs']
        }
        
        results = await self.checker._check_rule(self.test_path, rule)
        
        self.assertTrue(len(results) > 0)
        result = results[0]
        
        # Verifica estrutura do resultado
        self.assertEqual(result['rule_id'], 'TEST-001')
        self.assertEqual(result['category'], 'Test')
        self.assertEqual(result['severity'], 'high')
        self.assertFalse(result['compliant'])
        self.assertIn('violations', result)

    def test_is_relevant_file(self):
        """Testa verificação de relevância de arquivo"""
        test_cases = [
            # Regra com file_types
            ({
                'file_types': ['.cs', '.xaml']
            }, Path('test.cs'), True),
            ({
                'file_types': ['.cs', '.xaml']
            }, Path('test.txt'), False),
            
            # Regra com file_patterns
            ({
                'file_patterns': [r'.*Controller\.cs$']
            }, Path('UserController.cs'), True),
            ({
                'file_patterns': [r'.*Controller\.cs$']
            }, Path('User.cs'), False),
            
            # Regra sem restrições
            ({}, Path('any_file.txt'), True)
        ]
        
        for rule, file_path, expected in test_cases:
            result = self.checker._is_relevant_file(file_path, rule)
            self.assertEqual(
                result,
                expected,
                f"Failed for rule={rule}, file={file_path}"
            )

    def test_check_patterns(self):
        """Testa verificação de padrões"""
        content = '''
            public class TestClass {
                private string password = "123456";
                private string apiKey = "sk_test_123";
            }
        '''
        
        patterns = [
            r'password\s*=\s*["\'].*["\']',
            r'apiKey\s*=\s*["\'].*["\']'
        ]
        
        violations = self.checker._check_patterns(content, patterns)
        
        self.assertEqual(len(violations), 2)
        self.assertTrue(any('password' in v['match'] for v in violations))
        self.assertTrue(any('apiKey' in v['match'] for v in violations))

    def test_get_context(self):
        """Testa obtenção de contexto"""
        content = '''line 1
        line 2
        target line
        line 4
        line 5'''
        
        import re
        match = re.search(r'target line', content)
        context = self.checker._get_context(content, match, context_lines=1)
        
        self.assertEqual(len(context.splitlines()), 3)
        self.assertIn('line 2', context)
        self.assertIn('target line', context)
        self.assertIn('line 4', context)

    async def test_calculate_compliance_score(self):
        """Testa cálculo de score de compliance"""
        results = {
            'owasp_compliance': [
                {'compliant': True},
                {'compliant': False},
                {'compliant': True}
            ],
            'gdpr_compliance': [
                {'compliant': True},
                {'compliant': True}
            ],
            'best_practices': [
                {'compliant': False},
                {'compliant': False}
            ]
        }
        
        score = self.checker._calculate_compliance_score(results)
        
        # 4 compliant de 7 total = ~57%
        self.assertAlmostEqual(score, 57.14, places=2)
        
        # Teste com nenhum check
        empty_results = {
            'owasp_compliance': [],
            'gdpr_compliance': [],
            'best_practices': []
        }
        score = self.checker._calculate_compliance_score(empty_results)
        self.assertEqual(score, 0.0)

    async def test_generate_compliance_report(self):
        """Testa geração de relatório de compliance"""
        await self.asyncSetUp()
        
        # Primeiro faz verificação de compliance
        check_results = await self.checker.check_compliance(self.test_path)
        
        # Gera relatório
        report = await self.checker.generate_compliance_report(check_results)
        
        # Verifica estrutura do relatório
        self.assertIn('summary', report)
        self.assertIn('details', report)
        self.assertIn('recommendations', report)
        self.assertIn('timestamp', report)
        
        # Verifica summary
        summary = report['summary']
        self.assertIn('compliance_score', summary)
        self.assertIn('total_issues', summary)
        self.assertIn('critical_issues', summary)
        
        # Verifica details
        self.assertTrue(len(report['details']) > 0)
        for detail in report['details']:
            self.assertIn('category', detail)
            self.assertIn('description', detail)
            self.assertIn('severity', detail)
            
        # Verifica recommendations
        self.assertTrue(len(report['recommendations']) > 0)
        for rec in report['recommendations']:
            self.assertIn('category', rec)
            self.assertIn('description', rec)
            self.assertIn('priority', rec)

    def test_load_rules(self):
        """Testa carregamento de regras"""
        rules = self.checker._load_rules()
        
        # Verifica estrutura das regras
        self.assertIn('owasp', rules)
        self.assertIn('gdpr', rules)
        self.assertIn('security_best_practices', rules)
        
        # Verifica regras OWASP
        owasp_rules = rules['owasp']
        self.assertTrue(len(owasp_rules) > 0)
        for rule in owasp_rules:
            self.assertIn('id', rule)
            self.assertIn('category', rule)
            self.assertIn('severity', rule)
            self.assertIn('patterns', rule)
            
        # Verifica regras GDPR
        gdpr_rules = rules['gdpr']
        self.assertTrue(len(gdpr_rules) > 0)
        for rule in gdpr_rules:
            self.assertIn('id', rule)
            self.assertIn('category', rule)
            self.assertIn('patterns', rule)

if __name__ == '__main__':
    unittest.main()