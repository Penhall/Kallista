# tests/unit/core/test_state_manager.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime
from pathlib import Path
import json
import logging

from core.management.state_manager import StateManager

class TestStateManager(unittest.TestCase):
    def setUp(self):
        """Setup para cada teste"""
        self.config = {
            'persist_state': True,
            'state_file': 'test_state.json',
            'max_history': 100
        }
        self.state_manager = StateManager(self.config)

    def tearDown(self):
        """Limpeza após cada teste"""
        state_file = Path(self.config['state_file'])
        if state_file.exists():
            state_file.unlink()

    async def test_set_get_state(self):
        """Testa operações básicas de get/set"""
        # Set state
        key = "test_key"
        value = {"data": "test_value"}
        await self.state_manager.set_state(key, value)
        
        # Get state
        stored_value = await self.state_manager.get_state(key)
        self.assertEqual(stored_value, value)
        
        # Get nonexistent key
        with self.assertRaises(KeyError):
            await self.state_manager.get_state("nonexistent_key")

    async def test_update_state(self):
        """Testa atualização de estado"""
        key = "test_key"
        initial_value = {"count": 0}
        updated_value = {"count": 1}
        
        # Set initial state
        await self.state_manager.set_state(key, initial_value)
        
        # Update state
        await self.state_manager.update_state(key, updated_value)
        
        # Verify update
        stored_value = await self.state_manager.get_state(key)
        self.assertEqual(stored_value, updated_value)

    async def test_delete_state(self):
        """Testa deleção de estado"""
        key = "test_key"
        value = "test_value"
        
        # Set state
        await self.state_manager.set_state(key, value)
        
        # Delete state
        await self.state_manager.delete_state(key)
        
        # Verify deletion
        with self.assertRaises(KeyError):
            await self.state_manager.get_state(key)

    async def test_clear_state(self):
        """Testa limpeza completa do estado"""
        # Set multiple states
        test_data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        for key, value in test_data.items():
            await self.state_manager.set_state(key, value)
        
        # Clear all state
        await self.state_manager.clear_state()
        
        # Verify all states are cleared
        for key in test_data:
            with self.assertRaises(KeyError):
                await self.state_manager.get_state(key)

    async def test_state_history(self):
        """Testa histórico de estados"""
        key = "test_key"
        values = ["value1", "value2", "value3"]
        
        # Set state multiple times
        for value in values:
            await self.state_manager.set_state(key, value)
        
        # Get history
        history = await self.state_manager.get_state_history(key)
        
        # Verify history length
        self.assertEqual(len(history), len(values))
        
        # Verify history values
        for i, entry in enumerate(history):
            self.assertEqual(entry['value'], values[i])

    async def test_state_persistence(self):
        """Testa persistência de estado"""
        key = "test_key"
        value = "test_value"
        
        # Set state
        await self.state_manager.set_state(key, value)
        
        # Force persistence
        await self.state_manager._persist_state()
        
        # Create new state manager
        new_manager = StateManager(self.config)
        await new_manager._load_state()
        
        # Verify state was loaded
        stored_value = await new_manager.get_state(key)
        self.assertEqual(stored_value, value)

    async def test_state_validation(self):
        """Testa validação de estado"""
        # Test with invalid key
        with self.assertRaises(ValueError):
            await self.state_manager.set_state("", "value")
        
        # Test with None key
        with self.assertRaises(ValueError):
            await self.state_manager.set_state(None, "value")
        
        # Test with None value
        await self.state_manager.set_state("key", None)  # Should allow None values

    async def test_concurrent_access(self):
        """Testa acesso concorrente"""
        key = "test_key"
        iterations = 100
        
        async def update_state():
            for i in range(iterations):
                current = await self.state_manager.get_state(key, 0)
                await self.state_manager.set_state(key, current + 1)
        
        # Initialize state
        await self.state_manager.set_state(key, 0)
        
        # Run concurrent updates
        tasks = [update_state() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # Verify final value
        final_value = await self.state_manager.get_state(key)
        self.assertEqual(final_value, iterations * 5)

    async def test_state_limits(self):
        """Testa limites do estado"""
        # Set small max_history
        self.state_manager.config['max_history'] = 2
        
        key = "test_key"
        values = ["value1", "value2", "value3"]
        
        # Set state multiple times
        for value in values:
            await self.state_manager.set_state(key, value)
        
        # Get history
        history = await self.state_manager.get_state_history(key)
        
        # Verify history is limited
        self.assertEqual(len(history), 2)
        self.assertEqual(history[-1]['value'], values[-1])

    async def test_state_events(self):
        """Testa eventos de estado"""
        events = []
        
        # Register event handler
        async def state_changed(event):
            events.append(event)
            
        self.state_manager.on_state_changed(state_changed)
        
        # Set state
        key = "test_key"
        value = "test_value"
        await self.state_manager.set_state(key, value)
        
        # Verify event was fired
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['key'], key)
        self.assertEqual(events[0]['value'], value)
        self.assertEqual(events[0]['type'], 'set')

    def _verify_log_message(self, mock_logger, expected_message, level=logging.INFO):
        """Helper para verificar mensagens de log"""
        mock_logger.log.assert_called_with(level, expected_message)