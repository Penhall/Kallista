# core/management/context_manager.py
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ExecutionContext:
    agent_id: str
    task_id: str
    start_time: datetime
    parameters: Dict[str, Any]
    status: str = "initialized"
    result: Optional[Any] = None

class ContextManager:
    def __init__(self):
        self.active_contexts: Dict[str, ExecutionContext] = {}
        self.global_context: Dict[str, Any] = {}

    def create_context(self, agent_id: str, task_id: str, parameters: Dict[str, Any]) -> str:
        """Cria um novo contexto de execução"""
        context_id = f"{agent_id}_{task_id}_{datetime.now().timestamp()}"
        context = ExecutionContext(
            agent_id=agent_id,
            task_id=task_id,
            start_time=datetime.now(),
            parameters=parameters
        )
        self.active_contexts[context_id] = context
        return context_id

    def update_context(self, context_id: str, updates: Dict[str, Any]) -> None:
        """Atualiza um contexto existente"""
        if context_id in self.active_contexts:
            context = self.active_contexts[context_id]
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)

    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Recupera um contexto pelo ID"""
        if context_id in self.active_contexts:
            return asdict(self.active_contexts[context_id])
        return None

    def set_global_context(self, key: str, value: Any) -> None:
        """Define um valor no contexto global"""
        self.global_context[key] = value

    def get_global_context(self, key: str) -> Optional[Any]:
        """Recupera um valor do contexto global"""
        return self.global_context.get(key)

    def close_context(self, context_id: str, result: Any = None) -> None:
        """Finaliza um contexto de execução"""
        if context_id in self.active_contexts:
            self.active_contexts[context_id].status = "completed"
            self.active_contexts[context_id].result = result