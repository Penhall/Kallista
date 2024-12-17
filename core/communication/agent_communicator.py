# core/communication/agent_communicator.py
from typing import Dict, List, Any, Callable
from datetime import datetime
import asyncio
import json
from pathlib import Path

class Message:
    def __init__(self, sender: str, receiver: str, content: Any, message_type: str):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now()
        self.id = f"{sender}_{receiver}_{self.timestamp.timestamp()}"

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat()
        }

class AgentCommunicator:
    def __init__(self):
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[Message] = []
        self.log_path = Path("logs/communication")
        self.log_path.mkdir(parents=True, exist_ok=True)

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Registra um handler para um tipo específico de mensagem"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    async def send_message(self, message: Message) -> None:
        """Envia uma mensagem para a fila"""
        await self.message_queue.put(message)
        self.message_history.append(message)
        self._log_message(message)

    async def process_messages(self) -> None:
        """Processa mensagens da fila"""
        while True:
            message = await self.message_queue.get()
            handlers = self.message_handlers.get(message.message_type, [])
            
            for handler in handlers:
                try:
                    await handler(message)
                except Exception as e:
                    print(f"Erro ao processar mensagem {message.id}: {str(e)}")
            
            self.message_queue.task_done()

    def _log_message(self, message: Message) -> None:
        """Registra mensagem em arquivo"""
        log_file = self.log_path / f"messages_{datetime.now().strftime('%Y%m%d')}.json"
        with open(log_file, 'a') as f:
            json.dump(message.to_dict(), f)
            f.write('\n')

    def get_message_history(self, 
                          sender: str = None, 
                          receiver: str = None, 
                          message_type: str = None) -> List[Message]:
        """Recupera histórico de mensagens com filtros opcionais"""
        messages = self.message_history
        
        if sender:
            messages = [m for m in messages if m.sender == sender]
        if receiver:
            messages = [m for m in messages if m.receiver == receiver]
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
            
        return messages