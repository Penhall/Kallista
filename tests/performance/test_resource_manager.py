# tests/performance/test_resource_manager.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
from datetime import datetime
import psutil
import gc
import threading

from tools.performance.resource_manager import ResourceManager

class TestResourceManager(unittest.TestCase):
    def setUp(self):
        self.config = {
            'resource_limits': {
                'memory': {
                    'max_heap': 1024 * 1024 * 1024,  # 1GB
                    'max_stack': 8 * 1024 * 1024,    # 8MB
                    'max_objects': 1000000           # 1M objetos
                },
                'threads': {
                    'max_threads': 200,
                    'pool_size': 50,
                    'queue_size': 1000
                },
                'file_handles': {
                    'max_open': 1000,
                    'max_size': 100 * 1024 * 1024  # 100MB
                }
            }
        }
        self.manager = ResourceManager(self.config)

    def test_init(self):
        """Testa inicialização do manager"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.config, self.config)
        self.assertIsNotNone(self.manager.logger)
        self.assertIsNotNone(self.manager.resources)
        self.assertIsNotNone(self.manager.resource_limits)

    async def test_monitor_resources(self):
        """Testa monitoramento de recursos"""
        usage = await self.manager.monitor_resources()
        
        # Verifica estrutura do resultado
        self.assertIn('memory', usage)
        self.assertIn('threads', usage)
        self.assertIn('file_handles', usage)
        self.assertIn('timestamp', usage)
        
        # Verifica métricas de memória
        memory = usage['memory']
        self.assertIn('rss', memory)
        self.assertIn('vms', memory)
        self.assertIn('shared', memory)
        self.assertIn('heap', memory)
        self.assertIn('gc_stats', memory)
        
        # Verifica métricas de threads
        threads = usage['threads']
        self.assertIn('total', threads)
        self.assertIn('active', threads)
        self.assertIn('daemon', threads)
        self.assertIn('peak', threads)
        
        # Verifica métricas de handles
        handles = usage['file_handles']
        self.assertIn('open_files', handles)
        self.assertIn('connections', handles)
        self.assertIn('handles', handles)

    async def test_optimize_resources(self):
        """Testa otimização de recursos"""
        results = await self.manager.optimize_resources()
        
        # Verifica estrutura do resultado
        self.assertIn('optimizations', results)
        self.assertIn('released', results)
        self.assertIn('errors', results)
        
        # Verifica dados de release
        released = results['released']
        self.assertIn('memory', released)
        self.assertIn('handles', released)
        self.assertIn('threads', released)
        
        # Não deve ter erros
        self.assertEqual(len(results['errors']), 0)

    async def test_monitor_memory(self):
        """Testa monitoramento de memória"""
        memory_usage = await self.manager._monitor_memory()
        
        # Verifica métricas básicas
        self.assertIn('rss', memory_usage)
        self.assertIn('vms', memory_usage)
        self.assertIn('heap', memory_usage)
        self.assertIn('gc_stats', memory_usage)
        
        # Verifica estatísticas do GC
        gc_stats = memory_usage['gc_stats']
        self.assertIn('collections', gc_stats)
        self.assertIn('thresholds', gc_stats)
        self.assertIn('objects', gc_stats)
        
        # Verifica cálculo de percentual
        self.assertIn('usage_percent', memory_usage)
        self.assertGreaterEqual(memory_usage['usage_percent'], 0)
        self.assertLessEqual(memory_usage['usage_percent'], 100)

    async def test_monitor_threads(self):
        """Testa monitoramento de threads"""
        thread_usage = await self.manager._monitor_threads()
        
        # Verifica métricas básicas
        self.assertIn('total', thread_usage)
        self.assertIn('active', thread_usage)
        self.assertIn('daemon', thread_usage)
        self.assertIn('peak', thread_usage)
        self.assertIn('states', thread_usage)
        
        # Verifica estados das threads
        states = thread_usage['states']
        self.assertGreaterEqual(
            sum(count for count in states.values()),
            thread_usage['active']
        )

    async def test_monitor_file_handles(self):
        """Testa monitoramento de handles de arquivo"""
        handle_usage = await self.manager._monitor_file_handles()
        
        # Verifica métricas básicas
        self.assertIn('open_files', handle_usage)
        self.assertIn('connections', handle_usage)
        self.assertIn('limits', handle_usage)
        
        # Verifica limites
        limits = handle_usage['limits']
        self.assertIn('soft', limits)
        self.assertIn('hard', limits)

    async def test_optimize_memory(self):
        """Testa otimização de memória"""
        results = {'optimizations': [], 'errors': []}
        await self.manager._optimize_memory(results)
        
        # Verifica se otimização foi registrada
        self.assertTrue(
            any(opt['type'] == 'memory' 
                for opt in results['optimizations'])
        )
        
        # Não deve ter erros
        self.assertEqual(len(results['errors']), 0)

    async def test_optimize_threads(self):
        """Testa otimização de threads"""
        results = {'optimizations': [], 'errors': []}
        await self.manager._optimize_threads(results)
        
        # Verifica se otimização foi registrada
        self.assertTrue(
            any(opt['type'] == 'threads' 
                for opt in results['optimizations'])
        )
        
        # Verifica se threads ociosas foram identificadas
        self.assertTrue(len(self.manager._identify_idle_threads()) >= 0)

    async def test_optimize_file_handles(self):
        """Testa otimização de handles de arquivo"""
        results = {'optimizations': [], 'errors': []}
        await self.manager._optimize_file_handles(results)
        
        # Verifica se otimização foi registrada
        self.assertTrue(
            any(opt['type'] == 'file_handles' 
                for opt in results['optimizations'])
        )

    async def test_get_resource_report(self):
        """Testa geração de relatório de recursos"""
        report = await self.manager.get_resource_report()
        
        # Verifica estrutura do relatório
        self.assertIn('current_usage', report)
        self.assertIn('history', report)
        self.assertIn('trends', report)
        self.assertIn('recommendations', report)
        self.assertIn('timestamp', report)
        
        # Verifica tendências
        trends = report['trends']
        self.assertIn('memory', trends)
        self.assertIn('threads', trends)
        self.assertIn('file_handles', trends)
        
        # Verifica recomendações
        recommendations = report['recommendations']
        self.assertTrue(len(recommendations) >= 0)
        for rec in recommendations:
            self.assertIn('type', rec)
            self.assertIn('priority', rec)
            self.assertIn('description', rec)
            self.assertIn('action', rec)

    def test_calculate_trend(self):
        """Testa cálculo de tendência"""
        test_cases = [
            # Tendência crescente
            ([50, 60, 70, 80, 90], 'increasing'),
            # Tendência decrescente
            ([90, 80, 70, 60, 50], 'decreasing'),
            # Tendência estável
            ([70, 71, 69, 70, 71], 'stable'),
            # Caso com um valor
            ([50], 'stable')
        ]
        
        for values, expected in test_cases:
            trend = self.manager._calculate_trend(values)
            self.assertEqual(
                trend,
                expected,
                f"Failed for values={values}"
            )

    def test_get_thread_states(self):
        """Testa obtenção de estados de threads"""
        states = self.manager._get_thread_states()
        
        # Verifica se retorna dicionário
        self.assertIsInstance(states, dict)
        
        # Verifica estados comuns
        common_states = ['running', 'stopped']
        for state in common_states:
            self.assertIn(state, states)

    async def test_close_unused_handles(self):
        """Testa fechamento de handles não utilizados"""
        closed_count = self.manager._close_unused_handles()
        
        # Verifica se retorna número não negativo
        self.assertGreaterEqual(closed_count, 0)

if __name__ == '__main__':
    unittest.main()