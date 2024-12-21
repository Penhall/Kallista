# core/communication/agent_communicator.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, AsyncIterator
from datetime import datetime
import asyncio
import json
import uuid
from pathlib import Path

class MessageType(Enum):
    """Tipos de mensagens suportadas pelo sistema"""
    TASK = "TASK"
    NOTIFICATION = "NOTIFICATION"
    ERROR = "ERROR"
    BROADCAST = "BROADCAST"

@dataclass
class Message:
    """Classe que representa uma mensagem no sistema"""
    sender: str
    receiver: str
    content: Dict[str, Any]
    message_type: MessageType
    priority: str = "medium"
    require_ack: bool = False
    max_retries: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    ack_by: Optional[str] = None
    delivered: bool = False
    retry_count: int = 0

class AgentCommunicator:
    """Classe responsável pela comunicação entre agentes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.messages: Dict[str, Message] = {}
        self.handlers: Dict[MessageType, List[Callable]] = {}
        self._load_messages()

    async def send_message(self, message: Message) -> str:
        """Envia uma mensagem"""
        self._validate_message(message)
        self.messages[message.id] = message
        await self._persist_messages()
        return message.id

    async def get_message(self, message_id: str) -> Message:
        """Recupera uma mensagem pelo ID"""
        if message_id not in self.messages:
            raise KeyError(f"Message {message_id} not found")
        return self.messages[message_id]

    async def receive_messages(self, receiver: str) -> List[Message]:
        """Recebe mensagens para um destinatário específico"""
        return [
            msg for msg in self.messages.values()
            if msg.receiver in [receiver, '*'] and not msg.delivered
        ]

    async def broadcast_message(self, message: Message) -> None:
        """Envia uma mensagem em broadcast"""
        if message.message_type != MessageType.BROADCAST:
            raise ValueError("Message must be of type BROADCAST")
        await self.send_message(message)

    async def acknowledge_message(self, message_id: str, ack_by: str) -> None:
        """Confirma o recebimento de uma mensagem"""
        message = await self.get_message(message_id)
        message.acknowledged = True
        message.ack_by = ack_by
        await self._persist_messages()

    def register_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Registra um handler para um tipo de mensagem"""
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)

    async def _process_messages(self) -> None:
        """Processa mensagens usando os handlers registrados"""
        for message in self.messages.values():
            if message.message_type in self.handlers:
                for handler in self.handlers[message.message_type]:
                    await handler(message)

    async def _cleanup_expired(self) -> None:
        """Remove mensagens expiradas"""
        now = datetime.now()
        expired = [
            msg_id for msg_id, msg in self.messages.items()
            if (now - msg.timestamp).total_seconds() > self.config['message_ttl']
        ]
        for msg_id in expired:
            del self.messages[msg_id]
        await self._persist_messages()

    def _validate_message(self, message: Message) -> None:
        """Valida uma mensagem"""
        if not message.sender:
            raise ValueError("Message must have a sender")
        if not message.receiver:
            raise ValueError("Message must have a receiver")
        if message.content is None:
            raise ValueError("Message must have content")
        if not isinstance(message.message_type, MessageType):
            raise ValueError("Invalid message type")

    async def _persist_messages(self) -> None:
        """Persiste mensagens em arquivo"""
        if not self.config.get('persist_messages'):
            return
        
        messages_data = {
            msg_id: {
                'sender': msg.sender,
                'receiver': msg.receiver,
                'content': msg.content,
                'message_type': msg.message_type.value,
                'timestamp': msg.timestamp.isoformat(),
                # ... outros campos
            }
            for msg_id, msg in self.messages.items()
        }
        
        with open(self.config['messages_file'], 'w') as f:
            json.dump(messages_data, f)

    def _load_messages(self) -> None:
        """Carrega mensagens do arquivo"""
        if not self.config.get('persist_messages'):
            return
            
        try:
            with open(self.config['messages_file'], 'r') as f:
                messages_data = json.load(f)
                
            self.messages = {
                msg_id: Message(
                    sender=data['sender'],
                    receiver=data['receiver'],
                    content=data['content'],
                    message_type=MessageType(data['message_type']),
                    id=msg_id,
                    timestamp=datetime.fromisoformat(data['timestamp'])
                )
                for msg_id, data in messages_data.items()
            }
        except FileNotFoundError:
            self.messages = {}

    # Métodos adicionais necessários pelos testes
    async def filter_messages(self, receiver: str, filters: Dict[str, Any]) -> List[Message]:
        """Filtra mensagens por critérios específicos"""
        messages = await self.receive_messages(receiver)
        return [
            msg for msg in messages
            if all(getattr(msg, k) == v for k, v in filters.items())
        ]

    async def send_messages_batch(self, messages: List[Message]) -> List[str]:
        """Envia múltiplas mensagens em lote"""
        message_ids = []
        for message in messages:
            message_id = await self.send_message(message)
            message_ids.append(message_id)
        return message_ids

    async def receive_messages_batch(self, receiver: str) -> List[Message]:
        """Recebe múltiplas mensagens em lote"""
        return await self.receive_messages(receiver)

    async def get_message_history(self, sender: str, receiver: str) -> List[Message]:
        """Obtém histórico de mensagens entre dois agentes"""
        return [
            msg for msg in self.messages.values()
            if msg.sender == sender and msg.receiver == receiver
        ]

    async def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das mensagens"""
        stats = {
            'total_messages': len(self.messages),
            'messages_by_type': {}
        }
        
        for msg_type in MessageType:
            stats['messages_by_type'][msg_type.value] = len([
                msg for msg in self.messages.values()
                if msg.message_type == msg_type
            ])
        
        return stats