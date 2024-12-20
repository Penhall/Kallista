# tests/system/test_performance.py
import unittest
import asyncio
from pathlib import Path
import json
import time
from datetime import datetime
import psutil
import gc

from kallista.core import KallistaSystem
from tools.performance.performance_monitor import PerformanceMonitor

class TestKallistaPerformance(unittest.TestCase):
    def setUp(self):
        """Setup para os testes de performance"""
        self.config = {
            'base_dir': 'test_performance',
            'output_dir': 'test_output',
            'logs_dir': 'test_logs',
            'performance_thresholds': {
                'project_creation_time': 60,  # segundos
                'max_memory_usage': 1024 * 1024 * 1024,  # 1GB
                'max_cpu_usage': 80,  # percentual
                'response_time': 2.0  # segundos
            }
        }
        
        # Cria diretórios necessários
        for dir_name in self.config.values():
            if isinstance(dir_name, str):
                Path(dir_name).mkdir(exist_ok=True)
        
        # Inicializa sistema e monitor
        self.system = KallistaSystem(self.config)
        self.monitor = PerformanceMonitor()

    def tearDown(self):
        """Limpeza após os testes"""
        # Remove diretórios de teste
        for dir_name in self.config.values():
            if isinstance(dir_name, str) and Path(dir_name).exists():
                shutil.rmtree(dir_name)
        
        # Força coleta de lixo
        gc.collect()

   # tests/system/test_performance.py (continuação)
    async def test_project_creation_performance(self):
        """Testa performance na criação de projetos"""
        # Configuração do projeto
        project_config = {
            'name': 'PerformanceTest',
            'type': 'WPF',
            'features': ['user_authentication', 'data_persistence', 'reporting']
        }
        
        # Inicia monitoramento
        with self.monitor.track_operation('project_creation'):
            # Executa criação do projeto
            result = await self.system.create_project(project_config)
        
        # Obtém métricas
        metrics = self.monitor.get_metrics()
        
        # Verifica tempo de execução
        self.assertLess(
            metrics['execution_time'],
            self.config['performance_thresholds']['project_creation_time']
        )
        
        # Verifica uso de memória
        self.assertLess(
            metrics['max_memory_used'],
            self.config['performance_thresholds']['max_memory_usage']
        )
        
        # Verifica uso de CPU
        self.assertLess(
            metrics['max_cpu_usage'],
            self.config['performance_thresholds']['max_cpu_usage']
        )

    async def test_concurrent_operations(self):
        """Testa performance em operações concorrentes"""
        # Prepara múltiplos projetos
        projects = [
            {
                'name': f'ConcurrentTest_{i}',
                'type': 'WPF',
                'features': ['user_authentication']
            } for i in range(5)
        ]
        
        # Inicia monitoramento
        with self.monitor.track_operation('concurrent_operations'):
            # Executa criações em paralelo
            tasks = [
                self.system.create_project(config)
                for config in projects
            ]
            results = await asyncio.gather(*tasks)
        
        # Obtém métricas
        metrics = self.monitor.get_metrics()
        
        # Verifica sucesso das operações
        self.assertTrue(all(r['success'] for r in results))
        
        # Verifica métricas de concorrência
        self.assertIn('concurrent_operations', metrics)
        self.assertEqual(
            metrics['concurrent_operations']['total'],
            len(projects)
        )
        
        # Verifica uso de recursos
        self.assertLess(
            metrics['max_memory_used'],
            self.config['performance_thresholds']['max_memory_usage']
        )

    async def test_resource_usage(self):
        """Testa uso de recursos durante operações intensivas"""
        # Configuração do projeto complexo
        project_config = {
            'name': 'ResourceTest',
            'type': 'WPF',
            'features': [
                'user_authentication',
                'data_persistence',
                'reporting',
                'file_management',
                'real_time_updates'
            ],
            'ui': {
                'forms': [{'name': f'Form_{i}', 'fields': ['field1', 'field2']}
                         for i in range(20)]  # Muitos formulários
            },
            'database': {
                'entities': [{'name': f'Entity_{i}', 'properties': [
                    {'name': 'Id', 'type': 'int'},
                    {'name': 'Name', 'type': 'string'}
                ]} for i in range(20)]  # Muitas entidades
            }
        }
        
        # Inicia monitoramento
        with self.monitor.track_operation('resource_usage'):
            # Executa criação do projeto
            result = await self.system.create_project(project_config)
        
        # Obtém métricas
        metrics = self.monitor.get_metrics()
        
        # Verifica uso de memória ao longo do tempo
        memory_samples = metrics['memory_samples']
        self.assertTrue(len(memory_samples) > 0)
        self.assertTrue(all(
            sample <= self.config['performance_thresholds']['max_memory_usage']
            for sample in memory_samples
        ))
        
        # Verifica vazamentos de memória
        self.assertLess(
            abs(memory_samples[-1] - memory_samples[0]),
            50 * 1024 * 1024  # 50MB de tolerância
        )
        
        # Verifica uso de CPU
        cpu_samples = metrics['cpu_samples']
        self.assertTrue(all(
            sample <= self.config['performance_thresholds']['max_cpu_usage']
            for sample in cpu_samples
        ))

    async def test_response_times(self):
        """Testa tempos de resposta do sistema"""
        # Prepara operações para teste
        operations = [
            ('create_view', {'name': 'TestView', 'fields': ['field1', 'field2']}),
            ('create_model', {'name': 'TestModel', 'properties': ['prop1', 'prop2']}),
            ('create_viewmodel', {'name': 'TestViewModel', 'commands': ['cmd1', 'cmd2']})
        ]
        
        response_times = {}
        
        # Executa operações e mede tempos
        for op_name, op_config in operations:
            with self.monitor.track_operation(op_name):
                await getattr(self.system, op_name)(op_config)
            
            # Registra tempo de resposta
            metrics = self.monitor.get_metrics()
            response_times[op_name] = metrics['execution_time']
        
        # Verifica tempos de resposta
        for op_name, time in response_times.items():
            self.assertLess(
                time,
                self.config['performance_thresholds']['response_time'],
                f"Operation {op_name} exceeded response time threshold"
            )

    async def test_memory_management(self):
        """Testa gestão de memória durante operações longas"""
        # Configuração inicial de memória
        initial_memory = psutil.Process().memory_info().rss
        
        # Executa operações que consomem memória
        operations = 100
        metrics_list = []
        
        for i in range(operations):
            # Cria projeto pequeno
            project_config = {
                'name': f'MemoryTest_{i}',
                'type': 'WPF',
                'features': ['basic_ui']
            }
            
            with self.monitor.track_operation(f'iteration_{i}'):
                await self.system.create_project(project_config)
            
            # Coleta métricas
            metrics = self.monitor.get_metrics()
            metrics_list.append(metrics)
            
            # Força GC periodicamente
            if i % 10 == 0:
                gc.collect()
        
        # Memória final
        final_memory = psutil.Process().memory_info().rss
        
        # Análise de métricas
        memory_growth = [m['memory_used'] for m in metrics_list]
        max_growth_rate = max(
            (b - a) / a * 100
            for a, b in zip(memory_growth[:-1], memory_growth[1:])
        )
        
        # Verifica contenção de memória
        self.assertLess(max_growth_rate, 10)  # Máximo 10% de crescimento
        self.assertLess(
            final_memory - initial_memory,
            100 * 1024 * 1024  # 100MB de tolerância
        )

    async def test_scalability(self):
        """Testa escalabilidade do sistema"""
        # Testes com diferentes cargas
        workloads = [1, 5, 10, 20]
        execution_times = []
        
        for load in workloads:
            projects = [
                {
                    'name': f'ScaleTest_{i}',
                    'type': 'WPF',
                    'features': ['user_authentication']
                } for i in range(load)
            ]
            
            start_time = time.time()
            
            # Executa projetos em paralelo
            tasks = [
                self.system.create_project(config)
                for config in projects
            ]
            results = await asyncio.gather(*tasks)
            
            execution_time = time.time() - start_time
            execution_times.append(execution_time)
            
            # Verifica sucesso
            self.assertTrue(all(r['success'] for r in results))
        
        # Análise de escalabilidade
        # Verifica se o tempo não cresce linearmente com a carga
        scaling_factor = execution_times[-1] / execution_times[0]
        load_factor = workloads[-1] / workloads[0]
        
        self.assertLess(
            scaling_factor / load_factor,
            0.8,  # Espera-se escala sub-linear
            "System does not scale well with increased load"
        )

if __name__ == '__main__':
    unittest.main()