# core/management/state_manager.py
from typing import Dict, Any
from dataclasses import dataclass
import json

@dataclass
class SystemState:
    active_agents: Dict[str, Any]
    current_tasks: Dict[str, Any]
    resources: Dict[str, Any]

class StateManager:
    def __init__(self):
        self.state = SystemState(
            active_agents={},
            current_tasks={},
            resources={}
        )

    def update_state(self, key: str, value: Any) -> None:
        """Atualiza um estado específico do sistema"""
        if hasattr(self.state, key):
            setattr(self.state, key, value)

    def get_state(self, key: str) -> Any:
        """Recupera um estado específico do sistema"""
        return getattr(self.state, key) if hasattr(self.state, key) else None

    def save_state(self, filepath: str) -> None:
        """Salva o estado atual em um arquivo"""
        with open(filepath, 'w') as f:
            json.dump(self.state.__dict__, f)

    def load_state(self, filepath: str) -> None:
        """Carrega o estado de um arquivo"""
        with open(filepath, 'r') as f:
            state_dict = json.load(f)
            self.state = SystemState(**state_dict)