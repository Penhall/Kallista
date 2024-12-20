# tests/system/test_special_cases.py
import unittest
import asyncio
from pathlib import Path
import json
import shutil
from datetime import datetime
import signal
import tempfile
import random

from kallista.core import KallistaSystem
from core.management.state_manager import StateManager
from core.management.context_manager import ContextManager
from core.management.memory_manager import MemoryManager
from core.communication.agent_communicator import AgentCommunicator

class TestKallistaSpecialCases(unittest.TestCase):
    def setUp(self):
        """Setup para os testes de casos especiais"""
        self.config = {
            'base_dir': 'test_special',
            'output_dir': 'test_output',
            'logs_dir': 'test_logs',
            'temp_dir': 'test_temp',
            'recovery_enabled': True
        }
        
        # Cria diretórios necessários
        for dir_name in self.config.values():
            if isinstance(dir_name, str):
                Path(dir_name).mkdir(exist_ok=True)
        
        # Inicializa sistema e componentes
        self.system = KallistaSystem(self.config)
        self.state_manager = StateManager(self.config)
        self.context_manager = ContextManager(self.config)
        self.memory_manager = MemoryManager(self.config)
        self.communicator = AgentCommunicator(self.config)

    def tearDown(self):
        """Limpeza após os testes"""
        # Remove diretórios de teste
        for dir_name in self.config.values():
            if isinstance(dir_name, str):
                if Path(dir_name).exists():
                    shutil.rmtree(dir_name)

    async def test_system_recovery(self):
        """Testa recuperação do sistema após falha"""
        # Inicia criação de projeto
        project_config = {
            'name': 'RecoveryTest',
            'type': 'WPF',
            'features': ['user_authentication']
        }
        
        # Simula falha durante execução
        async def simulate_crash():
            result = await self.system.create_project(project_config)
            # Simula crash no meio do processo
            await self.system.simulate_crash()
            return result
        
        # Executa com tratamento de erro
        try:
            await simulate_crash()
        except Exception as e:
            self.assertIn('system_crash', str(e))
        
        # Tenta recuperar sistema
        recovery_result = await self.system.recover()
        
        # Verifica recuperação
        self.assertTrue(recovery_result['success'])
        self.assertIsNotNone(recovery_result['recovered_state'])
        self.assertTrue(recovery_result['data_integrity'])
        
        # Verifica se projeto foi completado
        project_path = Path(self.config['output_dir']) / 'RecoveryTest'
        self.assertTrue(project_path.exists())
        self.assertTrue((project_path / 'RecoveryTest.sln').exists())

    async def test_partial_failure_handling(self):
        """Testa tratamento de falhas parciais"""
        # Configura projeto com múltiplos componentes
        project_config = {
            'name': 'PartialFailureTest',
            'type': 'WPF',
            'features': ['user_authentication', 'data_persistence'],
            'components': [
                {'name': 'Component1', 'type': 'module'},
                {'name': 'Component2', 'type': 'module'},
                {'name': 'Component3', 'type': 'module'}
            ]
        }
        
        # Simula falha em um componente
        self.system.inject_failure('Component2')
        
        # Executa criação
        result = await self.system.create_project(project_config)
        
        # Verifica tratamento parcial
        self.assertTrue(result['partial_success'])
        self.assertEqual(len(result['failed_components']), 1)
        self.assertEqual(result['failed_components'][0], 'Component2')
        
        # Verifica componentes bem-sucedidos
        self.assertTrue(
            (Path(result['project_path']) / 'Component1').exists()
        )
        self.assertTrue(
            (Path(result['project_path']) / 'Component3').exists()
        )
        
       # tests/system/test_special_cases.py (continuação)
        # Verifica logs de falha
        log_file = Path(self.config['logs_dir']) / 'partial_failure.log'
        log_content = log_file.read_text()
        self.assertIn('Component2 creation failed', log_content)
        self.assertIn('Continuing with remaining components', log_content)

    async def test_state_corruption_recovery(self):
        """Testa recuperação de corrupção de estado"""
        # Cria estado inicial
        state_data = {
            'project_name': 'CorruptionTest',
            'status': 'in_progress',
            'components': ['comp1', 'comp2', 'comp3']
        }
        await self.state_manager.set_state('project_state', state_data)
        
        # Simula corrupção de estado
        await self.state_manager.corrupt_state('project_state')
        
        # Tenta recuperar estado
        recovery_result = await self.state_manager.recover_state('project_state')
        
        # Verifica recuperação
        self.assertTrue(recovery_result['success'])
        self.assertEqual(
            recovery_result['recovered_data']['project_name'],
            'CorruptionTest'
        )
        
        # Verifica backup
        backup_file = Path(self.config['temp_dir']) / 'state_backup.json'
        self.assertTrue(backup_file.exists())
        
        # Verifica logs de recuperação
        log_file = Path(self.config['logs_dir']) / 'state_recovery.log'
        log_content = log_file.read_text()
        self.assertIn('State corruption detected', log_content)
        self.assertIn('Recovery successful', log_content)

    async def test_resource_exhaustion(self):
        """Testa comportamento sob exaustão de recursos"""
        # Configura limite baixo de recursos
        self.config['resource_limits'] = {
            'max_memory': 100 * 1024 * 1024,  # 100MB
            'max_threads': 5,
            'max_file_handles': 10
        }
        
        # Cria projeto que excederá limites
        project_config = {
            'name': 'ResourceTest',
            'type': 'WPF',
            'features': ['user_authentication'],
            'components': [{'name': f'Component_{i}', 'type': 'module'}
                         for i in range(20)]  # Muitos componentes
        }
        
        # Executa com monitoramento de recursos
        with self.monitor_resources():
            result = await self.system.create_project(project_config)
        
        # Verifica adaptação
        self.assertTrue(result['adapted_execution'])
        self.assertIn('resource_management', result)
        
        resource_management = result['resource_management']
        self.assertTrue(resource_management['batched_processing'])
        self.assertTrue(resource_management['memory_optimization'])
        
        # Verifica logs de recursos
        self.assertIn('Resource limit approached', self.get_recent_logs())
        self.assertIn('Adapting execution strategy', self.get_recent_logs())

    async def test_network_interruption(self):
        """Testa comportamento durante interrupções de rede"""
        # Configura projeto que requer recursos externos
        project_config = {
            'name': 'NetworkTest',
            'type': 'WPF',
            'features': ['external_services'],
            'dependencies': {
                'nuget_packages': ['External.Package'],
                'api_references': ['ExternalAPI']
            }
        }
        
        # Simula interrupções de rede
        async def simulate_network_issues():
            await asyncio.sleep(random.uniform(0.1, 0.5))
            raise ConnectionError("Network unavailable")
        
        # Injeta simulação
        self.system.inject_network_simulator(simulate_network_issues)
        
        # Executa criação com retry policy
        result = await self.system.create_project_with_retry(
            project_config,
            max_retries=3,
            retry_delay=1
        )
        
        # Verifica resultado
        self.assertTrue(result['success'])
        self.assertTrue(result['retry_occurred'])
        self.assertGreater(result['retry_count'], 0)
        
        # Verifica cache offline
        cache_dir = Path(self.config['temp_dir']) / 'offline_cache'
        self.assertTrue(cache_dir.exists())
        self.assertTrue((cache_dir / 'nuget_packages').exists())
        
        # Verifica logs de retry
        log_content = self.get_recent_logs()
        self.assertIn('Network interruption detected', log_content)
        self.assertIn('Retrying operation', log_content)

    async def test_inconsistent_state(self):
        """Testa detecção e correção de estados inconsistentes"""
        # Cria estados interdependentes
        await self.state_manager.set_state('project_config', {
            'name': 'StateTest',
            'status': 'in_progress'
        })
        
        await self.state_manager.set_state('component_states', {
            'comp1': 'completed',
            'comp2': 'in_progress'
        })
        
        # Força inconsistência
        await self.state_manager.set_state('project_config', {
            'name': 'StateTest',
            'status': 'completed'  # Inconsistente com component_states
        })
        
        # Verifica detecção
        validation = await self.system.validate_state_consistency()
        
        self.assertFalse(validation['consistent'])
        self.assertGreater(len(validation['inconsistencies']), 0)
        
        # Corrige inconsistências
        correction = await self.system.correct_state_consistency()
        
        self.assertTrue(correction['success'])
        self.assertTrue(correction['state_valid'])
        
        # Verifica estados corrigidos
        project_state = await self.state_manager.get_state('project_config')
        self.assertEqual(project_state['status'], 'in_progress')

    async def test_concurrent_modifications(self):
        """Testa modificações concorrentes no projeto"""
        # Cria projeto inicial
        result = await self.system.create_project({
            'name': 'ConcurrencyTest',
            'type': 'WPF',
            'features': ['basic_ui']
        })
        
        # Prepara modificações concorrentes
        modifications = [
            {
                'type': 'add_component',
                'component': {'name': f'Component_{i}', 'type': 'module'}
            } for i in range(5)
        ]
        
        # Executa modificações concorrentemente
        tasks = [
            self.system.modify_project(result['project_id'], mod)
            for mod in modifications
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verifica resultados
        successful_mods = [r for r in results if not isinstance(r, Exception)]
        self.assertGreater(len(successful_mods), 0)
        
        # Verifica integridade
        validation = await self.system.validate_project(result['project_id'])
        self.assertTrue(validation['valid'])
        
        # Verifica logs de concorrência
        log_content = self.get_recent_logs()
        self.assertIn('Concurrent modification detected', log_content)
        self.assertIn('Applying concurrency control', log_content)

    def monitor_resources(self):
        """Context manager para monitoramento de recursos"""
        class ResourceMonitor:
            def __init__(self, test_case):
                self.test_case = test_case
                self.start_resources = None
                self.end_resources = None

            async def __aenter__(self):
                self.start_resources = self.get_resource_usage()
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.end_resources = self.get_resource_usage()
                self.test_case.resource_usage = {
                    'start': self.start_resources,
                    'end': self.end_resources,
                    'diff': self.calculate_diff()
                }

            def get_resource_usage(self):
                import psutil
                process = psutil.Process()
                return {
                    'memory': process.memory_info().rss,
                    'cpu': process.cpu_percent(),
                    'threads': process.num_threads(),
                    'files': len(process.open_files())
                }

            def calculate_diff(self):
                return {
                    k: self.end_resources[k] - self.start_resources[k]
                    for k in self.start_resources
                }

        return ResourceMonitor(self)

    def get_recent_logs(self):
        """Obtém logs recentes"""
        log_file = Path(self.config['logs_dir']) / 'system.log'
        if not log_file.exists():
            return ""
        
        with open(log_file) as f:
            # Retorna últimas 1000 linhas
            lines = f.readlines()[-1000:]
            return "".join(lines)

if __name__ == '__main__':
    unittest.main()