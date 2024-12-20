# tests/unit/core/test_context_manager.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from pathlib import Path
import json
import uuid

from core.management.context_manager import ContextManager

class TestContextManager(unittest.TestCase):
    def setUp(self):
        """Setup para cada teste"""
        self.config = {
            'max_contexts': 100,       # Máximo de contextos ativos
            'context_ttl': 3600,       # Tempo de vida do contexto em segundos
            'persist_contexts': True,   # Persiste contextos em disco
            'contexts_file': 'test_contexts.json'  # Arquivo de persistência
        }
        self.context_manager = ContextManager(self.config)

    def tearDown(self):
        """Limpeza após cada teste"""
        contexts_file = Path(self.config['contexts_file'])
        if contexts_file.exists():
            contexts_file.unlink()

    async def test_create_context(self):
        """Testa criação de contexto"""
        # Dados do contexto
        context_data = {
            'agent_id': 'test_agent',
            'task_id': 'test_task',
            'parameters': {'param1': 'value1'}
        }
        
        # Cria contexto
        context_id = await self.context_manager.create_context(**context_data)
        
        # Verifica se foi criado
        self.assertIsNotNone(context_id)
        context = await self.context_manager.get_context(context_id)
        
        # Verifica dados
        self.assertEqual(context['agent_id'], context_data['agent_id'])
        self.assertEqual(context['task_id'], context_data['task_id'])
        self.assertEqual(context['parameters'], context_data['parameters'])
        self.assertEqual(context['status'], 'active')

    async def test_update_context(self):
        """Testa atualização de contexto"""
        # Cria contexto inicial
        context_id = await self.context_manager.create_context(
            agent_id='test_agent',
            task_id='test_task'
        )
        
        # Dados de atualização
        update_data = {
            'status': 'completed',
            'result': {'output': 'test_output'}
        }
        
        # Atualiza contexto
        await self.context_manager.update_context(context_id, update_data)
        
        # Verifica atualização
        context = await self.context_manager.get_context(context_id)
        self.assertEqual(context['status'], update_data['status'])
        self.assertEqual(context['result'], update_data['result'])

    async def test_delete_context(self):
        """Testa deleção de contexto"""
        # Cria contexto
        context_id = await self.context_manager.create_context(
            agent_id='test_agent',
            task_id='test_task'
        )
        
        # Verifica existência
        self.assertIsNotNone(await self.context_manager.get_context(context_id))
        
        # Deleta contexto
        await self.context_manager.delete_context(context_id)
        
        # Verifica deleção
        with self.assertRaises(KeyError):
            await self.context_manager.get_context(context_id)

    async def test_context_expiration(self):
        """Testa expiração de contexto"""
        # Configura TTL curto
        self.context_manager.config['context_ttl'] = 1
        
        # Cria contexto
        context_id = await self.context_manager.create_context(
            agent_id='test_agent',
            task_id='test_task'
        )
        
        # Verifica existência inicial
        self.assertIsNotNone(await self.context_manager.get_context(context_id))
        
        # Aguarda expiração
        await asyncio.sleep(1.1)
        
        # Força verificação de expiração
        await self.context_manager._cleanup_expired()
        
        # Verifica se expirou
        with self.assertRaises(KeyError):
            await self.context_manager.get_context(context_id)

    async def test_context_persistence(self):
        """Testa persistência de contextos"""
        # Cria contextos
        contexts = {
            'context1': {'agent_id': 'agent1', 'task_id': 'task1'},
            'context2': {'agent_id': 'agent2', 'task_id': 'task2'}
        }
        
        context_ids = []
        for context_data in contexts.values():
            context_id = await self.context_manager.create_context(**context_data)
            context_ids.append(context_id)
        
        # Força persistência
        await self.context_manager._persist_contexts()
        
        # Cria novo context manager
        new_manager = ContextManager(self.config)
        await new_manager._load_contexts()
        
        # Verifica contextos carregados
        for context_id in context_ids:
            context = await new_manager.get_context(context_id)
            self.assertIsNotNone(context)

    async def test_context_search(self):
        """Testa busca de contextos"""
        # Cria contextos de teste
        await self.context_manager.create_context(
            agent_id='agent1',
            task_id='task1',
            parameters={'type': 'test'}
        )
        await self.context_manager.create_context(
            agent_id='agent1',
            task_id='task2',
            parameters={'type': 'prod'}
        )
        await self.context_manager.create_context(
            agent_id='agent2',
            task_id='task3',
            parameters={'type': 'test'}
        )
        
        # Busca por agent_id
        agent1_contexts = await self.context_manager.search_contexts(
            {'agent_id': 'agent1'}
        )
        self.assertEqual(len(agent1_contexts), 2)
        
        # Busca por parâmetro
        test_contexts = await self.context_manager.search_contexts(
            {'parameters.type': 'test'}
        )
        self.assertEqual(len(test_contexts), 2)

    async def test_context_hierarchy(self):
        """Testa hierarquia de contextos"""
        # Cria contexto pai
        parent_id = await self.context_manager.create_context(
            agent_id='parent_agent',
            task_id='parent_task'
        )
        
        # Cria contextos filhos
        child1_id = await self.context_manager.create_context(
            agent_id='child_agent1',
            task_id='child_task1',
            parent_id=parent_id
        )
        
        child2_id = await self.context_manager.create_context(
            agent_id='child_agent2',
            task_id='child_task2',
            parent_id=parent_id
        )
        
    # tests/unit/core/test_context_manager.py (continuação)
        # Verifica hierarquia (continuação)
        child1_context = await self.context_manager.get_context(child1_id)
        child2_context = await self.context_manager.get_context(child2_id)
        
        self.assertEqual(child1_context['parent_id'], parent_id)
        self.assertEqual(child2_context['parent_id'], parent_id)

    async def test_context_validation(self):
        """Testa validação de contexto"""
        # Testa criação com dados inválidos
        invalid_cases = [
            {'agent_id': '', 'task_id': 'task1'},  # agent_id vazio
            {'agent_id': 'agent1', 'task_id': ''},  # task_id vazio
            {'agent_id': None, 'task_id': 'task1'},  # agent_id None
            {'agent_id': 'agent1', 'task_id': None}  # task_id None
        ]
        
        for invalid_data in invalid_cases:
            with self.assertRaises(ValueError):
                await self.context_manager.create_context(**invalid_data)

    async def test_context_events(self):
        """Testa eventos de contexto"""
        events = []
        
        # Registra handler de eventos
        async def context_changed(event):
            events.append(event)
            
        self.context_manager.on_context_changed(context_changed)
        
        # Executa operações
        context_id = await self.context_manager.create_context(
            agent_id='test_agent',
            task_id='test_task'
        )
        
        await self.context_manager.update_context(
            context_id,
            {'status': 'completed'}
        )
        
        await self.context_manager.delete_context(context_id)
        
        # Verifica eventos
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]['type'], 'create')
        self.assertEqual(events[1]['type'], 'update')
        self.assertEqual(events[2]['type'], 'delete')

    async def test_context_limits(self):
        """Testa limites de contextos"""
        # Configura limite baixo
        self.context_manager.config['max_contexts'] = 2
        
        # Cria contextos até exceder limite
        context_ids = []
        for i in range(3):
            context_id = await self.context_manager.create_context(
                agent_id=f'agent_{i}',
                task_id=f'task_{i}'
            )
            context_ids.append(context_id)
        
        # Verifica se o contexto mais antigo foi removido
        with self.assertRaises(KeyError):
            await self.context_manager.get_context(context_ids[0])
        
        # Verifica se os contextos mais recentes existem
        self.assertIsNotNone(await self.context_manager.get_context(context_ids[1]))
        self.assertIsNotNone(await self.context_manager.get_context(context_ids[2]))

    async def test_context_statistics(self):
        """Testa estatísticas de contextos"""
        # Cria alguns contextos
        for i in range(3):
            await self.context_manager.create_context(
                agent_id=f'agent_{i}',
                task_id=f'task_{i}',
                status='active'
            )
            
        # Atualiza status de um contexto
        context_id = await self.context_manager.create_context(
            agent_id='agent_completed',
            task_id='task_completed',
            status='completed'
        )
        
        # Obtém estatísticas
        stats = await self.context_manager.get_statistics()
        
        # Verifica estatísticas
        self.assertEqual(stats['total_contexts'], 4)
        self.assertEqual(stats['active_contexts'], 3)
        self.assertEqual(stats['completed_contexts'], 1)
        self.assertIn('average_lifetime', stats)

    async def test_concurrent_context_operations(self):
        """Testa operações concorrentes em contextos"""
        # Cria contexto inicial
        context_id = await self.context_manager.create_context(
            agent_id='test_agent',
            task_id='test_task',
            value=0
        )
        
        async def update_context():
            for _ in range(10):
                context = await self.context_manager.get_context(context_id)
                value = context.get('value', 0)
                await self.context_manager.update_context(
                    context_id,
                    {'value': value + 1}
                )
                await asyncio.sleep(0.1)
        
        # Executa atualizações concorrentes
        tasks = [update_context() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # Verifica resultado final
        final_context = await self.context_manager.get_context(context_id)
        self.assertEqual(final_context['value'], 50)

    async def test_context_checkpointing(self):
        """Testa checkpointing de contextos"""
        # Cria contexto com dados iniciais
        context_id = await self.context_manager.create_context(
            agent_id='test_agent',
            task_id='test_task',
            data={'step': 1}
        )
        
        # Cria checkpoint
        checkpoint_id = await self.context_manager.create_checkpoint(context_id)
        
        # Atualiza contexto
        await self.context_manager.update_context(
            context_id,
            {'data': {'step': 2}}
        )
        
        # Restaura checkpoint
        await self.context_manager.restore_checkpoint(context_id, checkpoint_id)
        
        # Verifica restauração
        restored_context = await self.context_manager.get_context(context_id)
        self.assertEqual(restored_context['data']['step'], 1)

    async def test_context_isolation(self):
        """Testa isolamento entre contextos"""
        # Cria dois contextos
        context1_id = await self.context_manager.create_context(
            agent_id='agent1',
            task_id='task1',
            data={'shared_key': 'value1'}
        )
        
        context2_id = await self.context_manager.create_context(
            agent_id='agent2',
            task_id='task2',
            data={'shared_key': 'value2'}
        )
        
        # Modifica um contexto
        await self.context_manager.update_context(
            context1_id,
            {'data': {'shared_key': 'modified'}}
        )
        
        # Verifica isolamento
        context1 = await self.context_manager.get_context(context1_id)
        context2 = await self.context_manager.get_context(context2_id)
        
        self.assertEqual(context1['data']['shared_key'], 'modified')
        self.assertEqual(context2['data']['shared_key'], 'value2')

if __name__ == '__main__':
    unittest.main()