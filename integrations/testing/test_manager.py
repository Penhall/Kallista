# integrations/testing/test_manager.py
from typing import Dict, List, Optional, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    UI = "ui"
    PERFORMANCE = "performance"
    SECURITY = "security"

class TestStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"

class TestManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)
        self.results_path = Path("test_results")
        self.results_path.mkdir(exist_ok=True)

    async def run_tests(self, config: Dict) -> Dict:
        """Executa testes baseados na configuração"""
        try:
            test_run_id = f"test_run_{datetime.utcnow().timestamp()}"
            
            # Prepara ambiente de testes
            environment = await self._prepare_test_environment(config)
            
            results = {
                'id': test_run_id,
                'type': config.get('type', TestType.UNIT.value),
                'start_time': datetime.utcnow().isoformat(),
                'environment': environment,
                'results': {},
                'status': TestStatus.RUNNING.value
            }

            # Executa testes por tipo
            if config.get('run_unit', True):
                results['results']['unit'] = await self._run_unit_tests(config)
                
            if config.get('run_integration', False):
                results['results']['integration'] = await self._run_integration_tests(config)
                
            if config.get('run_ui', False):
                results['results']['ui'] = await self._run_ui_tests(config)
                
            if config.get('run_performance', False):
                results['results']['performance'] = await self._run_performance_tests(config)
                
            if config.get('run_security', False):
                results['results']['security'] = await self._run_security_tests(config)

            # Analisa resultados
            analysis = self._analyze_test_results(results['results'])
            results.update({
                'end_time': datetime.utcnow().isoformat(),
                'status': TestStatus.PASSED.value if analysis['success'] else TestStatus.FAILED.value,
                'summary': analysis
            })

            # Salva resultados
            await self._save_test_results(results)
            
            # Publica resultados
            await self._publish_test_results(results)

            return results

        except Exception as e:
            self.logger.error(f"Failed to run tests: {str(e)}")
            raise

    async def _run_unit_tests(self, config: Dict) -> Dict:
        """Executa testes unitários"""
        try:
            # Configura test runner
            test_runner = config.get('unit_test_runner', 'pytest')
            test_path = config.get('unit_test_path', 'tests/unit')
            
            if test_runner == 'pytest':
                command = f"pytest {test_path} --junitxml=test_results/unit_tests.xml"
            elif test_runner == 'dotnet':
                command = f"dotnet test {test_path} --logger:trx"
            else:
                raise ValueError(f"Unsupported test runner: {test_runner}")

            # Executa testes
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            # Processa resultados
            results = await self._process_test_results(
                test_type=TestType.UNIT,
                exit_code=process.returncode,
                stdout=stdout,
                stderr=stderr
            )

            return results

        except Exception as e:
            self.logger.error(f"Failed to run unit tests: {str(e)}")
            raise

    async def _run_integration_tests(self, config: Dict) -> Dict:
        """Executa testes de integração"""
        try:
            # Configura ambiente de integração
            await self._setup_integration_environment(config)
            
            # Executa testes
            test_path = config.get('integration_test_path', 'tests/integration')
            command = f"pytest {test_path} --junitxml=test_results/integration_tests.xml"
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            # Processa resultados
            results = await self._process_test_results(
                test_type=TestType.INTEGRATION,
                exit_code=process.returncode,
                stdout=stdout,
                stderr=stderr
            )

            # Limpa ambiente
            await self._cleanup_integration_environment(config)

            return results

        except Exception as e:
            self.logger.error(f"Failed to run integration tests: {str(e)}")
            raise

    async def _run_ui_tests(self, config: Dict) -> Dict:
        """Executa testes de UI"""
        try:
            # Configura ambiente de UI
            test_framework = config.get('ui_test_framework', 'selenium')
            test_path = config.get('ui_test_path', 'tests/ui')
            
            if test_framework == 'selenium':
                command = f"pytest {test_path} --driver Chrome --junitxml=test_results/ui_tests.xml"
            elif test_framework == 'playwright':
                command = f"pytest {test_path} --playwright --junitxml=test_results/ui_tests.xml"
            else:
                raise ValueError(f"Unsupported UI test framework: {test_framework}")

            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            # Processa resultados
            results = await self._process_test_results(
                test_type=TestType.UI,
                exit_code=process.returncode,
                stdout=stdout,
                stderr=stderr
            )

            return results

        except Exception as e:
            self.logger.error(f"Failed to run UI tests: {str(e)}")
            raise

    async def _run_performance_tests(self, config: Dict) -> Dict:
        """Executa testes de performance"""
        try:
            # Configura ambiente de performance
            test_tool = config.get('performance_test_tool', 'locust')
            test_path = config.get('performance_test_path', 'tests/performance')
            
            if test_tool == 'locust':
                command = f"locust -f {test_path}/locustfile.py --headless -u 10 -r 1 --run-time 1m"
            elif test_tool == 'k6':
                command = f"k6 run {test_path}/script.js"
            else:
                raise ValueError(f"Unsupported performance test tool: {test_tool}")

            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            # Processa resultados
            results = await self._process_test_results(
                test_type=TestType.PERFORMANCE,
                exit_code=process.returncode,
                stdout=stdout,
                stderr=stderr
            )

            return results

        except Exception as e:
            self.logger.error(f"Failed to run performance tests: {str(e)}")
            raise

    async def _run_security_tests(self, config: Dict) -> Dict:
        """Executa testes de segurança"""
        try:
            # Configura ferramentas de segurança
            security_tools = config.get('security_tools', ['bandit', 'safety'])
            results = {}

            for tool in security_tools:
                if tool == 'bandit':
                    command = "bandit -r . -f json -o test_results/bandit_results.json"
                elif tool == 'safety':
                    command = "safety check --json > test_results/safety_results.json"
                else:
                    continue

                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                # Processa resultados
                tool_results = await self._process_test_results(
                    test_type=TestType.SECURITY,
                    exit_code=process.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    tool=tool
                )
                results[tool] = tool_results

            return results

        except Exception as e:
            self.logger.error(f"Failed to run security tests: {str(e)}")
            raise

    def _analyze_test_results(self, results: Dict) -> Dict:
        """Analisa resultados dos testes"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        
        for test_type, type_results in results.items():
            if isinstance(type_results, dict):
                total_tests += type_results.get('total', 0)
                passed_tests += type_results.get('passed', 0)
                failed_tests += type_results.get('failed', 0)
                skipped_tests += type_results.get('skipped', 0)

        return {
            'success': failed_tests == 0,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }

    async def _save_test_results(self, results: Dict) -> None:
        """Salva resultados dos testes"""
        results_file = self.results_path / f"test_run_{results['id']}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)

    async def _publish_test_results(self, results: Dict) -> None:
        """Publica resultados dos testes"""
        try:
            # Publica no Azure DevOps
            if results.get('azure_project'):
                await self.azure.publish_test_results(results)

            # Publica no GitHub
            if results.get('github_repo'):
                await self.github.create_check_run({
                    'name': 'Test Results',
                    'head_sha': results.get('commit_sha'),
                    'status': 'completed',
                    'conclusion': 'success' if results['summary']['success'] else 'failure',
                    'output': {
                        'title': 'Test Results',
                        'summary': f"Total: {results['summary']['total_tests']}, "
                                 f"Passed: {results['summary']['passed_tests']}, "
                                 f"Failed: {results['summary']['failed_tests']}"
                    }
                })

        except Exception as e:
            self.logger.error(f"Failed to publish test results: {str(e)}")
            raise