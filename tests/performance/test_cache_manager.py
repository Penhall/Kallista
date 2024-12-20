# tests/performance/test_cache_manager.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
from datetime import datetime, timedelta
import pickle
import json
import threading
import time

from tools.performance.cache_manager import CacheManager

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.config = {
            'max_size': 1000,
            'max_memory': 100 * 1024 * 1024,  # 100MB
            'ttl': 3600,  # 1 hora
            'eviction_policy': 'lru',
            'persistent': False
        }
        self.cache_manager = CacheManager(self.config)

    def tearDown(self):
        """Limpa cache após cada teste"""
        asyncio.run(self.cache_manager.clear())

    def test_init(self):
        """Testa inicialização do cache manager"""
        self.assertIsNotNone(self.cache_manager)
        self.assertEqual(self.cache_manager.config, self.config)
        self.assertIsNotNone(self.cache_manager.cache)
        self.assertIsNotNone(self.cache_manager.metadata)
        self.assertIsNotNone(self.cache_manager.stats)
        self.assertIsNotNone(self.cache_manager.lock)

    async def test_get_set(self):
        """Testa operações básicas de get/set"""
        # Set inicial
        key = 'test_key'
        value = {'data': 'test_value'}
        success = await self.cache_manager.set(key, value)
        self.assertTrue(success)
        
        # Get do valor
        cached_value = await self.cache_manager.get(key)
        self.assertEqual(cached_value, value)
        
        # Get de chave inexistente
        missing_value = await self.cache_manager.get('nonexistent')
        self.assertIsNone(missing_value)
        
        # Verifica estatísticas
        self.assertEqual(self.cache_manager.stats['hits'], 1)
        self.assertEqual(self.cache_manager.stats['misses'], 1)

    async def test_ttl(self):
        """Testa expiração por TTL"""
        key = 'test_key'
        value = 'test_value'
        
        # Set com TTL curto
        await self.cache_manager.set(key, value, ttl=1)
        
        # Verifica valor imediatamente
        cached_value = await self.cache_manager.get(key)
        self.assertEqual(cached_value, value)
        
        # Aguarda expiração
        time.sleep(2)
        
        # Valor deve ter expirado
        expired_value = await self.cache_manager.get(key)
        self.assertIsNone(expired_value)

    async def test_max_size(self):
        """Testa limite de tamanho do cache"""
        # Configura cache pequeno
        self.cache_manager.config['max_size'] = 2
        
        # Adiciona itens até exceder limite
        await self.cache_manager.set('key1', 'value1')
        await self.cache_manager.set('key2', 'value2')
        await self.cache_manager.set('key3', 'value3')
        
        # Primeiro item deve ter sido removido (LRU)
        value1 = await self.cache_manager.get('key1')
        self.assertIsNone(value1)
        
        # Itens mais recentes devem existir
        value2 = await self.cache_manager.get('key2')
        value3 = await self.cache_manager.get('key3')
        self.assertEqual(value2, 'value2')
        self.assertEqual(value3, 'value3')

    async def test_eviction_lru(self):
        """Testa política de evicção LRU"""
        # Configura cache pequeno
        self.cache_manager.config['max_size'] = 3
        
        # Adiciona itens
        await self.cache_manager.set('key1', 'value1')
        await self.cache_manager.set('key2', 'value2')
        await self.cache_manager.set('key3', 'value3')
        
        # Acessa key1 para atualizar LRU
        await self.cache_manager.get('key1')
        
        # Adiciona novo item
        await self.cache_manager.set('key4', 'value4')
        
        # key2 deve ter sido removido (menos recentemente usado)
        value2 = await self.cache_manager.get('key2')
        self.assertIsNone(value2)
        
        # key1 deve existir (foi acessado recentemente)
        value1 = await self.cache_manager.get('key1')
        self.assertEqual(value1, 'value1')

    async def test_clear(self):
        """Testa limpeza do cache"""
        # Adiciona alguns itens
        await self.cache_manager.set('key1', 'value1')
        await self.cache_manager.set('key2', 'value2')
        
        # Limpa cache
        success = await self.cache_manager.clear()
        self.assertTrue(success)
        
        # Cache deve estar vazio
        self.assertEqual(len(self.cache_manager.cache), 0)
        self.assertEqual(len(self.cache_manager.metadata), 0)
        
        # Estatísticas devem estar zeradas
        self.assertEqual(self.cache_manager.stats['hits'], 0)
        self.assertEqual(self.cache_manager.stats['misses'], 0)
        self.assertEqual(self.cache_manager.stats['evictions'], 0)

    async def test_delete(self):
        """Testa remoção de item específico"""
        key = 'test_key'
        value = 'test_value'
        
        # Adiciona item
        await self.cache_manager.set(key, value)
        
        # Remove item
        success = await self.cache_manager.delete(key)
        self.assertTrue(success)
        
        # Item não deve existir
        cached_value = await self.cache_manager.get(key)
        self.assertIsNone(cached_value)

    async def test_persistence(self):
        """Testa persistência do cache"""
        # Configura cache persistente
        self.cache_manager.config['persistent'] = True
        
        # Adiciona itens
        await self.cache_manager.set('key1', 'value1')
        await self.cache_manager.set('key2', 'value2')
        
        # Força persistência
        self.cache_manager._persist_cache()
        
        # Cria novo cache manager
        new_cache = CacheManager({**self.config, 'persistent': True})
        new_cache._load_persistent_cache()
        
        # Verifica se dados foram carregados
        value1 = await new_cache.get('key1')
        value2 = await new_cache.get('key2')
        self.assertEqual(value1, 'value1')
        self.assertEqual(value2, 'value2')

    async def test_get_stats(self):
        """Testa obtenção de estatísticas"""
        # Gera algumas operações
        await self.cache_manager.set('key1', 'value1')
        await self.cache_manager.get('key1')  # hit
        await self.cache_manager.get('key2')  # miss
        
        stats = await self.cache_manager.get_stats()
        
        # Verifica estrutura das estatísticas
        self.assertIn('size', stats)
        self.assertIn('memory_usage', stats)
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('hit_ratio', stats)
        self.assertIn('evictions', stats)
        
        # Verifica valores
        self.assertEqual(stats['size'], 1)
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['hit_ratio'], 50.0)

    def test_calculate_hit_ratio(self):
        """Testa cálculo de taxa de acertos"""
        test_cases = [
            # hits, misses, expected_ratio
            (0, 0, 0.0),
            (10, 0, 100.0),
            (0, 10, 0.0),
            (75, 25, 75.0)
        ]
        
        for hits, misses, expected in test_cases:
            self.cache_manager.stats['hits'] = hits
            self.cache_manager.stats['misses'] = misses
            ratio = self.cache_manager._calculate_hit_ratio()
            self.assertEqual(ratio, expected)

    def test_get_size(self):
        """Testa cálculo de tamanho de objetos"""
        test_cases = [
            ('string', str.__sizeof__('string')),
            ({'key': 'value'}, {'key': 'value'}.__sizeof__()),
            ([1, 2, 3], [1, 2, 3].__sizeof__()),
            (123, 123.__sizeof__())
        ]
        
        for value, expected_size in test_cases:
            size = self.cache_manager._get_size(value)
            self.assertGreaterEqual(size, expected_size)

    async def test_maintenance(self):
        """Testa rotina de manutenção"""
        # Adiciona item com TTL curto
        await self.cache_manager.set('key1', 'value1', ttl=1)
        
        # Aguarda expiração e manutenção
        time.sleep(2)
        
        # Item deve ter sido removido
        value = await self.cache_manager.get('key1')
        self.assertIsNone(value)

    async def test_check_memory_limits(self):
        """Testa verificação de limites de memória"""
        # Configura limite baixo de memória
        self.cache_manager.config['max_memory'] = 100  # 100 bytes
        
        # Adiciona item grande
        large_value = 'x' * 200  # 200 bytes
        await self.cache_manager.set('large_key', large_value)
        
        # Aguarda verificação de limite
        time.sleep(1)
        
        # Item deve ter sido removido
        value = await self.cache_manager.get('large_key')
        self.assertIsNone(value)

if __name__ == '__main__':
    unittest.main()