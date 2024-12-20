# tests/security/test_code_sanitizer.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
import xml.etree.ElementTree as ET

from tools.security.code_sanitizer import CodeSanitizer

class TestCodeSanitizer(unittest.TestCase):
    def setUp(self):
        self.sanitizer = CodeSanitizer()
        self.test_path = Path("test_project")
        self.test_files = {
            'TestClass.cs': '''
                public class TestClass {
                    public string ProcessInput(string input) {
                        return input;  // Sem sanitização
                    }

                    public void ExecuteQuery(string userId) {
                        var query = "SELECT * FROM Users WHERE id = " + userId;
                        ExecuteCommand(query);
                    }

                    private void WriteOutput(string data) {
                        Response.Write(data);
                    }
                }
            ''',
            'MainWindow.xaml': '''
                <Window x:Class="TestApp.MainWindow"
                        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
                    <Grid>
                        <TextBox Text="{Binding UserInput}" />
                        <Button Content="Submit" Click="OnSubmitClick" />
                    </Grid>
                </Window>
            ''',
            'App.config': '''
                <?xml version="1.0"?>
                <configuration>
                    <connectionStrings>
                        <add name="Default" connectionString="Data Source=local;Password=123456;" />
                    </connectionStrings>
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
        """Testa inicialização do sanitizer"""
        self.assertIsNotNone(self.sanitizer)
        self.assertIsNotNone(self.sanitizer.sanitization_rules)
        self.assertIn('input_validation', self.sanitizer.sanitization_rules)
        self.assertIn('output_encoding', self.sanitizer.sanitization_rules)
        self.assertIn('data_protection', self.sanitizer.sanitization_rules)

    async def test_sanitize_project(self):
        """Testa sanitização completa do projeto"""
        await self.asyncSetUp()
        
        results = await self.sanitizer.sanitize_project(self.test_path)
        
        # Verifica estrutura do resultado
        self.assertIn('sanitized_files', results)
        self.assertIn('failed_files', results)
        self.assertIn('skipped_files', results)
        self.assertIn('timestamp', results)
        
        # Verifica se arquivos foram processados
        self.assertTrue(len(results['sanitized_files']) > 0)
        self.assertEqual(len(results['failed_files']), 0)

    async def test_sanitize_csharp(self):
        """Testa sanitização de código C#"""
        await self.asyncSetUp()
        
        content = self.test_files['TestClass.cs']
        changes = await self.sanitizer._sanitize_csharp(content)
        
        # Verifica mudanças na sanitização de input
        input_change = next(
            (c for c in changes if 'ProcessInput' in c['original']),
            None
        )
        self.assertIsNotNone(input_change)
        self.assertIn('SecurityHelper.SanitizeInput', input_change['sanitized'])
        
        # Verifica mudanças na query SQL
        sql_change = next(
            (c for c in changes if 'ExecuteQuery' in c['original']),
            None
        )
        self.assertIsNotNone(sql_change)
        self.assertIn('Parameters.AddWithValue', sql_change['sanitized'])
        
        # Verifica mudanças no output
        output_change = next(
            (c for c in changes if 'Response.Write' in c['original']),
            None
        )
        self.assertIsNotNone(output_change)
        self.assertIn('HtmlEncode', output_change['sanitized'])

    async def test_sanitize_xaml(self):
        """Testa sanitização de XAML"""
        await self.asyncSetUp()
        
        content = self.test_files['MainWindow.xaml']
        changes = await self.sanitizer._sanitize_xaml(content)
        
        # Verifica sanitização de binding
        binding_change = next(
            (c for c in changes if 'Binding UserInput' in c['original']),
            None
        )
        self.assertIsNotNone(binding_change)
        self.assertIn('Converter={StaticResource SecurityConverter}', binding_change['sanitized'])
        
        # Verifica sanitização de event handler
        event_change = next(
            (c for c in changes if 'Click=' in c['original']),
            None
        )
        self.assertIsNotNone(event_change)
        self.assertIn('SecureOnSubmitClick', event_change['sanitized'])

    async def test_sanitize_config(self):
        """Testa sanitização de configurações"""
        await self.asyncSetUp()
        
        content = self.test_files['App.config']
        changes = await self.sanitizer._sanitize_config(content)
        
        # Verifica sanitização de connection string
        conn_change = next(
            (c for c in changes if 'connectionString' in c['original']),
            None
        )
        self.assertIsNotNone(conn_change)
        self.assertIn('%%encrypted%%', conn_change['sanitized'])

    def test_should_sanitize(self):
        """Testa verificação de arquivos a serem sanitizados"""
        test_cases = [
            (Path('test.cs'), True),
            (Path('test.xaml'), True),
            (Path('test.config'), True),
            (Path('test.json'), True),
            (Path('test.dll'), False),
            (Path('.git/config'), False),
            (Path('bin/debug/app.exe'), False)
        ]
        
        for path, expected in test_cases:
            result = self.sanitizer._should_sanitize(path)
            self.assertEqual(
                result,
                expected,
                f"Failed for path={path}"
            )

    async def test_apply_changes(self):
        """Testa aplicação de mudanças em arquivo"""
        await self.asyncSetUp()
        
        test_file = self.test_path / "test.cs"
        test_file.write_text('''
            public string GetValue(string input) {
                return input;
            }
        ''')
        
        changes = [{
            'line': 2,
            'original': 'return input;',
            'sanitized': 'return SecurityHelper.SanitizeInput(input);'
        }]
        
        self.sanitizer._apply_changes(test_file, changes)
        
        # Verifica se as mudanças foram aplicadas
        content = test_file.read_text()
        self.assertIn('SecurityHelper.SanitizeInput', content)
        self.assertNotIn('return input;', content)

    async def test_sanitize_binding(self):
        """Testa sanitização de bindings XAML"""
        element = ET.Element('TextBox')
        element.set('Text', '{Binding UserInput}')
        
        changes = self.sanitizer._sanitize_binding(element, 'Text')
        
        self.assertTrue(len(changes) > 0)
        self.assertEqual(changes[0]['type'], 'binding_security')
        self.assertIn('SecurityConverter', changes[0]['sanitized'])

    async def test_sanitize_event_handler(self):
        """Testa sanitização de event handlers XAML"""
        element = ET.Element('Button')
        element.set('Click', 'OnSubmitClick')
        
        changes = self.sanitizer._sanitize_event_handler(element, 'Click')
        
        self.assertTrue(len(changes) > 0)
        self.assertEqual(changes[0]['type'], 'event_security')
        self.assertIn('Secure', changes[0]['sanitized'])

if __name__ == '__main__':
    unittest.main()