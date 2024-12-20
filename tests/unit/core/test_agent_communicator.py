# tests/unit/core/test_agent_communicator.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from pathlib import Path
import json
import uuid

from core.communication.agent_communicator import AgentCommunicator, Message, MessageType

class TestAgentCommunicator(unittest.TestCase):
    def setUp(self):
        """Setup para cada teste"""
        self.config = {
            'message_ttl': 3600,        # Tempo de vida das mensagens em segundos
            'max_queue_size': 1000,     # Tamanho máximo da fila
            'persist_messages': True,    # Persistência de mensagens
            'messages_file': 'test_messages.json'  # Arquivo de persistência
        }
        self.communicator = AgentCommunicator(self.config)

    def tearDown(self):
        """Limpeza após cada teste"""
        messages_file = Path(self.config['messages_file'])
        if messages_file.exists():
            messages_file.unlink()

    async def test_send_message(self):
        """Testa envio de mensagem"""
        # Cria mensagem
        message = Message(
            sender='agent1',
            receiver='agent2',
            content={'data': 'test'},
            message_type=MessageType.TASK
        )
        
        # Envia mensagem
        message_id = await self.communicator.send_message(message)
        
        # Verifica se foi enviada
        self.assertIsNotNone(message_id)
        sent_message = await self.communicator.get_message(message_id)
        self.assertEqual(sent_message.sender, message.sender)
        self.assertEqual(sent_message.receiver, message.receiver)
        self.assertEqual(sent_message.content, message.content)
        self.assertEqual(sent_message.message_type, message.message_type)

    async def test_receive_message(self):
        """Testa recebimento de mensagem"""
        # Envia mensagem
        message = Message(
            sender='agent1',
            receiver='agent2',
            content={'data': 'test'},
            message_type=MessageType.TASK
        )
        await self.communicator.send_message(message)
        
        # Recebe mensagem
        received_messages = await self.communicator.receive_messages('agent2')
        
        # Verifica mensagem recebida
        self.assertEqual(len(received_messages), 1)
        received = received_messages[0]
        self.assertEqual(received.sender, message.sender)
        self.assertEqual(received.content, message.content)

    async def test_message_expiration(self):
        """Testa expiração de mensagens"""
        # Configura TTL curto
        self.communicator.config['message_ttl'] = 1
        
        # Envia mensagem
        message = Message(
            sender='agent1',
            receiver='agent2',
            content={'data': 'test'},
            message_type=MessageType.TASK
        )
        message_id = await self.communicator.send_message(message)
        
        # Aguarda expiração
        await asyncio.sleep(1.1)
        
        # Força limpeza de mensagens expiradas
        await self.communicator._cleanup_expired()
        
        # Verifica se mensagem expirou
        with self.assertRaises(KeyError):
            await self.communicator.get_message(message_id)

    async def test_message_queue(self):
        """Testa fila de mensagens"""
        # Configura limite baixo
        self.communicator.config['max_queue_size'] = 2
        
        # Envia mensagens até exceder limite
        messages = []
        for i in range(3):
            message = Message(
                sender='agent1',
                receiver='agent2',
                content={'data': f'test_{i}'},
                message_type=MessageType.TASK
            )
            message_id = await self.communicator.send_message(message)
            messages.append(message_id)
        
        # Verifica se mensagem mais antiga foi removida
        with self.assertRaises(KeyError):
            await self.communicator.get_message(messages[0])
        
        # Verifica se mensagens mais recentes existem
        self.assertIsNotNone(await self.communicator.get_message(messages[1]))
        self.assertIsNotNone(await self.communicator.get_message(messages[2]))

    async def test_message_persistence(self):
        """Testa persistência de mensagens"""
        # Envia mensagens
        messages = []
        for i in range(2):
            message = Message(
                sender=f'agent{i}',
                receiver=f'agent{i+1}',
                content={'data': f'test_{i}'},
                message_type=MessageType.TASK
            )
            message_id = await self.communicator.send_message(message)
            messages.append(message_id)
        
        # Força persistência
        await self.communicator._persist_messages()
        
        # Cria novo communicator
        new_communicator = AgentCommunicator(self.config)
        await new_communicator._load_messages()
        
        # Verifica se mensagens foram carregadas
        for message_id in messages:
            message = await new_communicator.get_message(message_id)
            self.assertIsNotNone(message)

    async def test_broadcast_message(self):
        """Testa envio de mensagem em broadcast"""
        # Lista de receptores
        receivers = ['agent1', 'agent2', 'agent3']
        
        # Envia mensagem em broadcast
        broadcast_message = Message(
            sender='broadcast_agent',
            receiver='*',  # broadcast
            content={'data': 'broadcast_test'},
            message_type=MessageType.BROADCAST
        )
        await self.communicator.broadcast_message(broadcast_message)
        
        # Verifica recebimento para cada agente
        for receiver in receivers:
            messages = await self.communicator.receive_messages(receiver)
            self.assertEqual(len(messages), 1)
            received = messages[0]
            self.assertEqual(received.content, broadcast_message.content)
            self.assertEqual(received.message_type, MessageType.BROADCAST)

    async def test_message_handlers(self):
        """Testa handlers de mensagens"""
        handled_messages = []
        
        # Registra handler
        async def message_handler(message):
            handled_messages.append(message)
            
        self.communicator.register_handler(
            MessageType.TASK,
            message_handler
        )
        
        # Envia mensagens de diferentes tipos
        task_message = Message(
            sender='agent1',
            receiver='agent2',
            content={'data': 'task_test'},
            message_type=MessageType.TASK
        )
        
        notification_message = Message(
            sender='agent1',
            receiver='agent2',
            content={'data': 'notification_test'},
            message_type=MessageType.NOTIFICATION
        )
        
        await self.communicator.send_message(task_message)
        await self.communicator.send_message(notification_message)
        
        # Processa mensagens
        await self.communicator._process_messages()
        
        # Verifica se apenas mensagens do tipo TASK foram handled
        self.assertEqual(len(handled_messages), 1)
        handled = handled_messages[0]
        self.assertEqual(handled.message_type, MessageType.TASK)
        self.assertEqual(handled.content, task_message.content)

    # tests/unit/core/test_agent_communicator.py (continuação)
    async def test_message_filtering(self):
        """Testa filtragem de mensagens"""
        # Envia mensagens com diferentes prioridades
        messages = [
            Message(
                sender='agent1',
                receiver='agent2',
                content={'data': 'high_priority'},
                message_type=MessageType.TASK,
                priority='high'
            ),
            Message(
                sender='agent1',
                receiver='agent2',
                content={'data': 'medium_priority'},
                message_type=MessageType.TASK,
                priority='medium'
            ),
            Message(
                sender='agent1',
                receiver='agent2',
                content={'data': 'low_priority'},
                message_type=MessageType.TASK,
                priority='low'
            )
        ]
        
        for message in messages:
            await self.communicator.send_message(message)
        
        # Filtra mensagens por prioridade
        high_priority = await self.communicator.filter_messages(
            receiver='agent2',
            filters={'priority': 'high'}
        )
        
        # Verifica filtragem
        self.assertEqual(len(high_priority), 1)
        self.assertEqual(high_priority[0].content['data'], 'high_priority')

    async def test_message_acknowledgment(self):
        """Testa confirmação de recebimento de mensagens"""
        # Envia mensagem que requer confirmação
        message = Message(
            sender='agent1',
            receiver='agent2',
            content={'data': 'test'},
            message_type=MessageType.TASK,
            require_ack=True
        )
        
        message_id = await self.communicator.send_message(message)
        
        # Confirma recebimento
        await self.communicator.acknowledge_message(message_id, 'agent2')
        
        # Verifica status da mensagem
        message = await self.communicator.get_message(message_id)
        self.assertTrue(message.acknowledged)
        self.assertEqual(message.ack_by, 'agent2')

    async def test_message_history(self):
        """Testa histórico de mensagens"""
        # Envia várias mensagens
        sender = 'agent1'
        receiver = 'agent2'
        
        for i in range(3):
            message = Message(
                sender=sender,
                receiver=receiver,
                content={'data': f'test_{i}'},
                message_type=MessageType.TASK
            )
            await self.communicator.send_message(message)
        
        # Obtém histórico de mensagens
        history = await self.communicator.get_message_history(
            sender=sender,
            receiver=receiver
        )
        
        # Verifica histórico
        self.assertEqual(len(history), 3)
        for i, message in enumerate(history):
            self.assertEqual(message.content['data'], f'test_{i}')

    async def test_message_statistics(self):
        """Testa estatísticas de mensagens"""
        # Envia mensagens de diferentes tipos
        messages = [
            Message(
                sender='agent1',
                receiver='agent2',
                content={'data': 'task'},
                message_type=MessageType.TASK
            ),
            Message(
                sender='agent1',
                receiver='agent2',
                content={'data': 'notification'},
                message_type=MessageType.NOTIFICATION
            ),
            Message(
                sender='agent1',
                receiver='agent2',
                content={'data': 'error'},
                message_type=MessageType.ERROR
            )
        ]
        
        for message in messages:
            await self.communicator.send_message(message)
        
        # Obtém estatísticas
        stats = await self.communicator.get_statistics()
        
        # Verifica estatísticas
        self.assertEqual(stats['total_messages'], 3)
        self.assertEqual(stats['messages_by_type'][MessageType.TASK.value], 1)
        self.assertEqual(stats['messages_by_type'][MessageType.NOTIFICATION.value], 1)
        self.assertEqual(stats['messages_by_type'][MessageType.ERROR.value], 1)

    async def test_message_batch_operations(self):
        """Testa operações em lote"""
        # Prepara mensagens
        messages = [
            Message(
                sender='agent1',
                receiver='agent2',
                content={'data': f'test_{i}'},
                message_type=MessageType.TASK
            ) for i in range(3)
        ]
        
        # Envia mensagens em lote
        message_ids = await self.communicator.send_messages_batch(messages)
        
        # Verifica envio
        self.assertEqual(len(message_ids), 3)
        
        # Recebe mensagens em lote
        received = await self.communicator.receive_messages_batch('agent2')
        
        # Verifica recebimento
        self.assertEqual(len(received), 3)

    async def test_message_retry(self):
        """Testa retentativa de envio de mensagens"""
        # Configura mensagem com retentativas
        message = Message(
            sender='agent1',
            receiver='agent2',
            content={'data': 'test'},
            message_type=MessageType.TASK,
            max_retries=3
        )
        
        # Simula falhas e retentativas
        with patch.object(self.communicator, '_deliver_message') as mock_deliver:
            # Configura mock para falhar nas primeiras tentativas
            mock_deliver.side_effect = [
                Exception("Delivery failed"),
                Exception("Delivery failed"),
                None  # Sucesso na terceira tentativa
            ]
            
            # Tenta enviar mensagem
            message_id = await self.communicator.send_message(message)
            
            # Verifica número de tentativas
            self.assertEqual(mock_deliver.call_count, 3)
            
            # Verifica status final
            message = await self.communicator.get_message(message_id)
            self.assertTrue(message.delivered)

    async def test_message_validation(self):
        """Testa validação de mensagens"""
        # Testa mensagens inválidas
        invalid_cases = [
            # Sem remetente
            Message(
                sender='',
                receiver='agent2',
                content={'data': 'test'},
                message_type=MessageType.TASK
            ),
            # Sem destinatário
            Message(
                sender='agent1',
                receiver='',
                content={'data': 'test'},
                message_type=MessageType.TASK
            ),
            # Sem conteúdo
            Message(
                sender='agent1',
                receiver='agent2',
                content=None,
                message_type=MessageType.TASK
            ),
            # Tipo de mensagem inválido
            Message(
                sender='agent1',
                receiver='agent2',
                content={'data': 'test'},
                message_type='INVALID_TYPE'
            )
        ]
        
        # Verifica se cada caso inválido gera exceção
        for invalid_message in invalid_cases:
            with self.assertRaises(ValueError):
                await self.communicator.send_message(invalid_message)

if __name__ == '__main__':
    unittest.main()