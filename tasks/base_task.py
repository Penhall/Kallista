# tasks/base_task.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BaseTask(ABC):
    def __init__(self, name: str, description: str):
        self.task_id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Any:
        """Executa a tarefa"""
        pass

    @abstractmethod
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Valida se a tarefa pode ser executada"""
        pass

    def start(self):
        """Inicia a execução da tarefa"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self, result: Any):
        """Marca a tarefa como completa"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def fail(self, error: str):
        """Marca a tarefa como falha"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error

    def cancel(self):
        """Cancela a execução da tarefa"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Converte a tarefa para dicionário"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error': self.error,
            'metadata': self.metadata
        }