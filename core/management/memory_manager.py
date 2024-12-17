# core/management/memory_manager.py
from typing import Dict, List, Any
from datetime import datetime
import json
from pathlib import Path

class MemoryManager:
    def __init__(self):
        self.short_term_memory: Dict[str, Any] = {}
        self.long_term_memory: Dict[str, List[Dict]] = {}
        self.memory_path = Path("data/memory")
        self.memory_path.mkdir(parents=True, exist_ok=True)

    def store_short_term(self, key: str, value: Any) -> None:
        """Armazena informação na memória de curto prazo"""
        self.short_term_memory[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }

    def store_long_term(self, category: str, data: Dict) -> None:
        """Armazena informação na memória de longo prazo"""
        if category not in self.long_term_memory:
            self.long_term_memory[category] = []
        
        memory_entry = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.long_term_memory[category].append(memory_entry)
        self._persist_memory(category)

    def retrieve_short_term(self, key: str) -> Any:
        """Recupera informação da memória de curto prazo"""
        return self.short_term_memory.get(key, {}).get('value')

    def retrieve_long_term(self, category: str, filter_func=None) -> List[Dict]:
        """Recupera informações da memória de longo prazo"""
        memories = self.long_term_memory.get(category, [])
        if filter_func:
            return [m for m in memories if filter_func(m)]
        return memories

    def _persist_memory(self, category: str) -> None:
        """Persiste memória de longo prazo em arquivo"""
        file_path = self.memory_path / f"{category}_memory.json"
        with open(file_path, 'w') as f:
            json.dump(self.long_term_memory[category], f)

    def load_memory(self, category: str) -> None:
        """Carrega memória persistida"""
        file_path = self.memory_path / f"{category}_memory.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                self.long_term_memory[category] = json.load(f)

    def clear_short_term(self) -> None:
        """Limpa a memória de curto prazo"""
        self.short_term_memory.clear()