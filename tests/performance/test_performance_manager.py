# tests/performance/test_performance_manager.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
from datetime import datetime
import psutil
import gc
import threading

from tools.performance.performance_manager import PerformanceManager

class TestPerformanceManager(unittest.TestCase):
    def setUp(self):
        self.config = {
            'thresholds': {
                'cpu_usage': 80.0,
                'memory_usage': 85.0,
                'response_time': 2.0,
                'disk_usage': 90.0,
                'cache_size': 512,
                'thread_count': 200
            }
        }
        self.manager = PerformanceManager(self.config)

    def test_init(self):
        """Testa inicialização do manager"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.config, self.config)
        self.assertIsNotNone(self.manager.logger)
        self.assertIsNotNone(self.manager.metrics)
        self.assertIsNotNone(self.manager.thresholds)

    async def test_monitor_performance(self):
        """Testa monitoramento de performance"""
        results = await self.manager.monitor_performance()
        
        # Verifica estrutura do resultado
        self.assertIn('system_metrics', results)
        self.assertIn('application_metrics', results)
        self.assertIn('resource_usage', results)
        self.assertIn('bottlenecks', results)
        self.assertIn('recommendations', results)
        self.assertIn('timestamp', results)
        
        # Verifica métricas do sistema
        system_metrics = results['system_metrics']
        self.assertIn('cpu', system_metrics)
        self.assertIn('memory', system_metrics)
        self.assertIn('disk', system_metrics)
        self.assertIn('network', system_metrics)

    async def test_collect_system_metrics(self):
        """Testa coleta de métricas do sistema"""
        metrics = await self.manager._collect_system_metrics()
        
        # Verifica CPU metrics
        self.assertIn('cpu', metrics)
        cpu_metrics = metrics['cpu']
        self.assertIn('usage_percent', cpu_metrics)
        self.assertIn('count', cpu_metrics)
        self.assertIn('frequency', cpu_metrics)
        
        # Verifica Memory metrics
        self.assertIn('memory', metrics)
        memory_metrics = metrics['memory']
        self.assertIn('total', memory_metrics)
        self.assertIn('available', memory_metrics)
        self.assertIn('used_percent', memory_metrics)
        
        # Verifica Disk metrics
        self.assertIn('disk', metrics)
        disk_metrics = metrics['disk']
        self.assertIn('total', disk_metrics)
        self.assertIn('used', disk_metrics)
        self.assertIn('free', disk_metrics)
        self.assertIn('used_percent', disk_metrics)
        
        # Verifica Network metrics
        self.assertIn('network', metrics)
        network_metrics = metrics['network']
        self.assertIn('connections', network_metrics)
        self.assertIn('stats', network_metrics)

    async def test_collect_application_metrics(self):
        """Testa coleta de métricas da aplicação"""
        metrics = await self.manager._collect_application_metrics()
        
        # Verifica métricas do processo
        self.assertIn('process', metrics)
        process_metrics = metrics['process']
        self.assertIn('cpu_percent', process_metrics)
        self.assertIn('memory_info', process_metrics)
        self.assertIn('num_threads', process_metrics)
        self.assertIn('open_files', process_metrics)
        
        # Verifica métricas de threads
        self.assertIn('threads', metrics)
        thread_metrics = metrics['threads']
        self.assertIn('active', thread_metrics)
        self.assertIn('peak', thread_metrics)
        
        # Verifica métricas do GC
        self.assertIn('gc', metrics)
        gc_metrics = metrics['gc']
        self.assertIn('counts', gc_metrics)
        self.assertIn('thresholds', gc_metrics)

    async def test_collect_resource_usage(self):
        """Testa coleta de uso de recursos"""
        metrics = await self.manager._collect_resource_usage()
        
        # Verifica métricas
        self.assertIn('cache', metrics)
        self.assertIn('database', metrics)
        self.assertIn('files', metrics)
        self.assertIn('network', metrics)

    @patch('tools.performance.performance_manager.PerformanceManager._collect_system_metrics')
    async def test_identify_bottlenecks(self, mock_metrics):
        """Testa identificação de gargalos"""
        # Mock de métricas com valores altos
        mock_metrics.return_value = {
            'cpu': {'usage_percent': 90.0},
            'memory': {'used_percent': 95.0},
            'disk': {'used_percent': 92.0}
        }
        
        metrics = {
            'system_metrics': await mock_metrics(),
            'application_metrics': {
                'threads': {'active': 250}
            }
        }
        
        bottlenecks = await self.manager._identify_bottlenecks(metrics)
        
        # Deve identificar gargalos
        self.assertTrue(len(bottlenecks) > 0)
        
        # Verifica gargalo de CPU
        cpu_bottleneck = next(
            (b for b in bottlenecks if b['type'] == 'cpu'),
            None
        )
        self.assertIsNotNone(cpu_bottleneck)
        self.assertEqual(cpu_bottleneck['severity'], 'high')
        
        # Verifica gargalo de memória
        memory_bottleneck = next(
            (b for b in bottlenecks if b['type'] == 'memory'),
            None
        )
        self.assertIsNotNone(memory_bottleneck)
        self.assertEqual(memory_bottleneck['severity'], 'high')

    async def test_generate_recommendations(self):
        """Testa geração de recomendações"""
        bottlenecks = [
            {
                'type': 'cpu',
                'severity': 'high',
                'current_value': 90.0,
                'threshold': 80.0,
                'description': 'CPU usage above threshold'
            },
            {
                'type': 'memory',
                'severity': 'high',
                'current_value': 95.0,
                'threshold': 85.0,
                'description': 'Memory usage above threshold'
            }
        ]
        
        recommendations = await self.manager._generate_recommendations(bottlenecks)
        
        # Verifica recomendações
        self.assertTrue(len(recommendations) > 0)
        
        # Verifica recomendações de CPU
        cpu_recs = [r for r in recommendations if r['type'] == 'cpu']
        self.assertTrue(len(cpu_recs) > 0)
        for rec in cpu_recs:
            self.assertIn('priority', rec)
            self.assertIn('description', rec)
            self.assertIn('action', rec)
            
        # Verifica recomendações de memória
        memory_recs = [r for r in recommendations if r['type'] == 'memory']
        self.assertTrue(len(memory_recs) > 0)
        for rec in memory_recs:
            self.assertIn('priority', rec)
            self.assertIn('description', rec)
            self.assertIn('action', rec)

    async def test_optimize_performance(self):
        """Testa otimização de performance"""
        results = await self.manager.optimize_performance()
        
        # Verifica estrutura do resultado
        self.assertIn('optimizations', results)
        self.assertIn('errors', results)
        self.assertIn('timestamp', results)
        
        # Verifica otimizações realizadas
        optimizations = results['optimizations']
        self.assertTrue(len(optimizations) > 0)
        
        # Não deve ter erros
        self.assertEqual(len(results['errors']), 0)
        
        # Testa otimização específica
        memory_results = await self.manager.optimize_performance('memory')
        self.assertTrue(any(opt['type'] == 'memory' 
                          for opt in memory_results['optimizations']))

    def test_calculate_optimization_impact(self):
        """Testa cálculo de impacto da otimização"""
        before = {
            'system_metrics': {
                'cpu': {'usage_percent': 90.0},
                'memory': {'used_percent': 95.0},
                'disk': {'used_percent': 92.0}
            }
        }
        
        after = {
            'system_metrics': {
                'cpu': {'usage_percent': 70.0},
                'memory': {'used_percent': 75.0},
                'disk': {'used_percent': 82.0}
            }
        }
        
        impact = self.manager._calculate_optimization_impact(before, after)
        
        # Verifica estrutura do impacto
        self.assertIn('cpu', impact)
        self.assertIn('memory', impact)
        self.assertIn('disk', impact)
        
        # Verifica cálculos
        self.assertEqual(impact['cpu']['improvement'], 20.0)
        self.assertEqual(impact['memory']['improvement'], 20.0)
        self.assertEqual(impact['disk']['improvement'], 10.0)

    async def test_optimize_all(self):
        """Testa otimização completa"""
        results = {'errors': [], 'optimizations': []}
        await self.manager._optimize_all(results)
        
        # Verifica se não houve erros
        self.assertEqual(len(results['errors']), 0)
        
        # Verifica se houve otimizações
        self.assertTrue(len(results['optimizations']) > 0)

if __name__ == '__main__':
    unittest.main()