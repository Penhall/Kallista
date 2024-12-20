# tests/unit/core/test_memory_manager.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from pathlib import Path
import json
import gc

from core.management.memory_manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        """Setup para cada teste"""
        self.config = {
            'short_term_limit': 100,  # Limite de itens na memória de curto prazo
            'long_term_limit': 1000,  # Limite de itens na memória de longo prazo
            'persist_memory': True,   # Persiste memória em disco
            'memory_file': 'test_memory.json',  # Arquivo de persistência
            'gc_interval': 60         # Intervalo do garbage collector em segundos
        }
        self.memory_manager = MemoryManager(self.config)

    def tearDown(self):
        """Limpeza após cada teste"""
        memory_file = Path(self.config['memory_file'])
        if memory_file.exists():
            memory_file.unlink()

    async def test_store_retrieve_short_term(self):
        """Testa armazenamento e recuperação de curto prazo"""
        # Store in short-term memory
        key = "test_key"
        value = {"data": "test_value"}
        await self.memory_manager.store_short_term(key, value)
        
        # Retrieve from short-term memory
        stored_value = await self.memory_manager.retrieve(key)
        self.assertEqual(stored_value, value)
        
        # Verify it's in short-term memory
        self.assertIn(key, self.memory_manager.short_term_memory)
        self.assertNotIn(key, self.memory_manager.long_term_memory)

    async def test_store_retrieve_long_term(self):
        """Testa armazenamento e recuperação de longo prazo"""
        # Store in long-term memory
        key = "test_key"
        value = {"data": "test_value"}
        await self.memory_manager.store_long_term(key, value)
        
        # Retrieve from long-term memory
        stored_value = await self.memory_manager.retrieve(key)
        self.assertEqual(stored_value, value)
        
        # Verify it's in long-term memory
        self.assertIn(key, self.memory_manager.long_term_memory)
        self.assertNotIn(key, self.memory_manager.short_term_memory)

    async def test_memory_expiration(self):
        """Testa expiração de memória de curto prazo"""
        key = "test_key"
        value = "test_value"
        ttl = 1  # 1 segundo
        
        # Store with TTL
        await self.memory_manager.store_short_term(key, value, ttl)
        
        # Verify immediate retrieval
        stored_value = await self.memory_manager.retrieve(key)
        self.assertEqual(stored_value, value)
        
        # Wait for expiration
        await asyncio.sleep(ttl + 0.1)
        
        # Verify expired value
        expired_value = await self.memory_manager.retrieve(key)
        self.assertIsNone(expired_value)

    async def test_memory_promotion(self):
        """Testa promoção de memória de curto para longo prazo"""
        key = "test_key"
        value = "test_value"
        access_threshold = 5
        
        # Store in short-term memory
        await self.memory_manager.store_short_term(key, value)
        
        # Access multiple times
        for _ in range(access_threshold + 1):
            await self.memory_manager.retrieve(key)
        
        # Verify promotion to long-term memory
        self.assertIn(key, self.memory_manager.long_term_memory)
        self.assertNotIn(key, self.memory_manager.short_term_memory)

    async def test_memory_limits(self):
        """Testa limites de memória"""
        # Test short-term memory limit
        for i in range(self.config['short_term_limit'] + 1):
            await self.memory_manager.store_short_term(f"key_{i}", f"value_{i}")
        
        # Verify oldest item was removed
        self.assertEqual(
            len(self.memory_manager.short_term_memory),
            self.config['short_term_limit']
        )
        
        # Test long-term memory limit
        for i in range(self.config['long_term_limit'] + 1):
            await self.memory_manager.store_long_term(f"long_key_{i}", f"value_{i}")
        
        # Verify oldest item was removed
        self.assertEqual(
            len(self.memory_manager.long_term_memory),
            self.config['long_term_limit']
        )

    async def test_memory_persistence(self):
        """Testa persistência de memória"""
        # Store some values
        test_data = {
            "short_key": "short_value",
            "long_key": "long_value"
        }
        
        await self.memory_manager.store_short_term("short_key", test_data["short_key"])
        await self.memory_manager.store_long_term("long_key", test_data["long_key"])
        
        # Force persistence
        await self.memory_manager._persist_memory()
        
        # Create new memory manager
        new_manager = MemoryManager(self.config)
        await new_manager._load_memory()
        
        # Verify persistence
        for key, value in test_data.items():
            stored_value = await new_manager.retrieve(key)
            self.assertEqual(stored_value, value)

    async def test_memory_cleanup(self):
        """Testa limpeza de memória"""
        # Store items with different TTLs
        items = {
            "expire_1": {"ttl": 1, "value": "value1"},
            "expire_2": {"ttl": 2, "value": "value2"},
            "no_expire": {"ttl": None, "value": "value3"}
        }
        
        for key, data in items.items():
            await self.memory_manager.store_short_term(
                key,
                data["value"],
                data["ttl"]
            )
        
        # Wait for some items to expire
        await asyncio.sleep(1.5)
        
        # Force cleanup
        await self.memory_manager._cleanup_expired()
        
        # Verify expired items are removed
        self.assertIsNone(await self.memory_manager.retrieve("expire_1"))
        self.assertIsNotNone(await self.memory_manager.retrieve("expire_2"))
        self.assertIsNotNone(await self.memory_manager.retrieve("no_expire"))

    async def test_memory_statistics(self):
        """Testa estatísticas de memória"""
        # Store some test data
        await self.memory_manager.store_short_term("key1", "value1")
        await self.memory_manager.store_long_term("key2", "value2")
        
        # Get statistics
        stats = await self.memory_manager.get_statistics()
        
        # Verify statistics
        self.assertEqual(stats['short_term_count'], 1)
        self.assertEqual(stats['long_term_count'], 1)
        self.assertIn('total_size', stats)
        self.assertIn('hit_ratio', stats)
        self.assertIn('miss_ratio', stats)

   # tests/unit/core/test_memory_manager.py (continuação)
    async def test_memory_search(self):
        """Testa busca em memória"""
        # Armazena dados de teste
        test_data = {
            "user_1": {"name": "John", "age": 30},
            "user_2": {"name": "Jane", "age": 25},
            "product_1": {"name": "Laptop", "price": 1000}
        }
        
        for key, value in test_data.items():
            await self.memory_manager.store_short_term(key, value)
            
        # Busca por padrão
        user_results = await self.memory_manager.search("user_*")
        self.assertEqual(len(user_results), 2)
        
        # Busca por valor
        age_results = await self.memory_manager.search_by_value({"age": 30})
        self.assertEqual(len(age_results), 1)
        self.assertEqual(age_results[0]['key'], "user_1")

    async def test_bulk_operations(self):
        """Testa operações em massa"""
        # Dados de teste
        items = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        # Armazenamento em massa
        await self.memory_manager.store_many_short_term(items)
        
        # Verifica armazenamento
        for key, value in items.items():
            stored_value = await self.memory_manager.retrieve(key)
            self.assertEqual(stored_value, value)
            
        # Remove em massa
        keys_to_remove = ["key1", "key2"]
        await self.memory_manager.remove_many(keys_to_remove)
        
        # Verifica remoção
        for key in keys_to_remove:
            self.assertIsNone(await self.memory_manager.retrieve(key))
        
        # Verifica item não removido
        self.assertIsNotNone(await self.memory_manager.retrieve("key3"))

    async def test_memory_compression(self):
        """Testa compressão de memória"""
        # Ativa compressão
        self.memory_manager.config['use_compression'] = True
        
        # Dados grandes para teste
        large_data = "x" * 1000  # String de 1000 caracteres
        
        # Armazena com compressão
        await self.memory_manager.store_long_term("large_key", large_data)
        
        # Verifica se foi comprimido
        compressed_size = self.memory_manager._get_item_size(
            self.memory_manager.long_term_memory["large_key"]
        )
        self.assertLess(compressed_size, len(large_data))
        
        # Recupera e verifica dados
        retrieved_data = await self.memory_manager.retrieve("large_key")
        self.assertEqual(retrieved_data, large_data)

    async def test_memory_encryption(self):
        """Testa criptografia de memória"""
        # Ativa criptografia
        self.memory_manager.config['use_encryption'] = True
        
        # Dados sensíveis
        sensitive_data = {"password": "secret123"}
        
        # Armazena com criptografia
        await self.memory_manager.store_long_term("sensitive_key", sensitive_data)
        
        # Verifica se está criptografado na memória
        raw_data = self.memory_manager.long_term_memory["sensitive_key"]
        self.assertNotEqual(raw_data, sensitive_data)
        
        # Recupera e verifica dados
        retrieved_data = await self.memory_manager.retrieve("sensitive_key")
        self.assertEqual(retrieved_data, sensitive_data)

    async def test_memory_events(self):
        """Testa eventos de memória"""
        events = []
        
        # Registra handler de eventos
        async def memory_changed(event):
            events.append(event)
            
        self.memory_manager.on_memory_changed(memory_changed)
        
        # Executa operações
        await self.memory_manager.store_short_term("key1", "value1")
        await self.memory_manager.store_long_term("key2", "value2")
        await self.memory_manager.remove("key1")
        
        # Verifica eventos
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]['type'], 'store_short_term')
        self.assertEqual(events[1]['type'], 'store_long_term')
        self.assertEqual(events[2]['type'], 'remove')

    async def test_memory_metrics(self):
        """Testa métricas de memória"""
        # Executa operações para gerar métricas
        await self.memory_manager.store_short_term("key1", "value1")
        await self.memory_manager.retrieve("key1")
        await self.memory_manager.retrieve("nonexistent")
        
        # Obtém métricas
        metrics = await self.memory_manager.get_metrics()
        
        # Verifica métricas básicas
        self.assertEqual(metrics['operations']['stores'], 1)
        self.assertEqual(metrics['operations']['retrievals'], 2)
        self.assertEqual(metrics['hits'], 1)
        self.assertEqual(metrics['misses'], 1)
        
        # Verifica métricas de tamanho
        self.assertIn('memory_usage', metrics)
        self.assertIn('item_count', metrics)

    async def test_memory_serialization(self):
        """Testa serialização de diferentes tipos de dados"""
        test_cases = [
            ("string_key", "string_value"),
            ("int_key", 42),
            ("float_key", 3.14),
            ("list_key", [1, 2, 3]),
            ("dict_key", {"a": 1, "b": 2}),
            ("none_key", None),
            ("bool_key", True)
        ]
        
        # Testa armazenamento e recuperação de cada tipo
        for key, value in test_cases:
            # Armazena valor
            await self.memory_manager.store_long_term(key, value)
            
            # Recupera e verifica
            stored_value = await self.memory_manager.retrieve(key)
            self.assertEqual(stored_value, value)
            
            # Verifica tipo
            self.assertEqual(type(stored_value), type(value))

    async def test_concurrent_access(self):
        """Testa acesso concorrente à memória"""
        key = "concurrent_key"
        iterations = 100
        
        async def update_memory():
            for i in range(iterations):
                current = await self.memory_manager.retrieve(key, 0)
                await self.memory_manager.store_short_term(key, current + 1)
        
        # Inicializa valor
        await self.memory_manager.store_short_term(key, 0)
        
        # Executa atualizações concorrentes
        tasks = [update_memory() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # Verifica resultado final
        final_value = await self.memory_manager.retrieve(key)
        self.assertEqual(final_value, iterations * 5)

if __name__ == '__main__':
    unittest.main()