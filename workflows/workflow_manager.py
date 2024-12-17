# workflows/workflow_manager.py
from typing import Dict, List, Any, Optional
from enum import Enum
import uuid
from datetime import datetime
import asyncio
import json
from pathlib import Path

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class WorkflowManager:
    def __init__(self):
        self.workflows: Dict[str, 'Workflow'] = {}
        self.history_path = Path("data/workflows")
        self.history_path.mkdir(parents=True, exist_ok=True)

    async def create_workflow(self, name: str, tasks: List[Dict], config: Dict) -> str:
        """Cria um novo workflow"""
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(workflow_id, name, tasks, config)
        self.workflows[workflow_id] = workflow
        return workflow_id

    async def start_workflow(self, workflow_id: str) -> None:
        """Inicia a execução de um workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} não encontrado")
        
        workflow = self.workflows[workflow_id]
        await workflow.start()

    async def pause_workflow(self, workflow_id: str) -> None:
        """Pausa um workflow em execução"""
        if workflow_id in self.workflows:
            await self.workflows[workflow_id].pause()

    async def resume_workflow(self, workflow_id: str) -> None:
        """Retoma um workflow pausado"""
        if workflow_id in self.workflows:
            await self.workflows[workflow_id].resume()

    async def cancel_workflow(self, workflow_id: str) -> None:
        """Cancela um workflow"""
        if workflow_id in self.workflows:
            await self.workflows[workflow_id].cancel()

    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """Obtém o status de um workflow"""
        if workflow_id in self.workflows:
            return self.workflows[workflow_id].status
        return None

    def save_workflow_history(self, workflow: 'Workflow') -> None:
        """Salva o histórico do workflow"""
        history_file = self.history_path / f"{workflow.id}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(history_file, 'w') as f:
            json.dump(workflow.to_dict(), f, indent=4)

class Workflow:
    def __init__(self, workflow_id: str, name: str, tasks: List[Dict], config: Dict):
        self.id = workflow_id
        self.name = name
        self.tasks = tasks
        self.config = config
        self.status = WorkflowStatus.PENDING
        self.current_task_index = 0
        self.results: Dict[str, Any] = {}
        self.errors: List[Dict] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    async def start(self) -> None:
        """Inicia a execução do workflow"""
        self.status = WorkflowStatus.RUNNING
        self.start_time = datetime.now()
        await self._execute_tasks()

    async def pause(self) -> None:
        """Pausa o workflow"""
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.PAUSED

    async def resume(self) -> None:
        """Retoma o workflow"""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.RUNNING
            await self._execute_tasks()

    async def cancel(self) -> None:
        """Cancela o workflow"""
        self.status = WorkflowStatus.FAILED
        self.end_time = datetime.now()

    async def _execute_tasks(self) -> None:
        """Executa as tarefas do workflow"""
        while self.current_task_index < len(self.tasks):
            if self.status != WorkflowStatus.RUNNING:
                break

            current_task = self.tasks[self.current_task_index]
            try:
                result = await self._execute_task(current_task)
                self.results[current_task['id']] = result
            except Exception as e:
                self.errors.append({
                    'task_id': current_task['id'],
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                if not self.config.get('continue_on_error', False):
                    self.status = WorkflowStatus.FAILED
                    break

            self.current_task_index += 1

        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.COMPLETED
        self.end_time = datetime.now()

    async def _execute_task(self, task: Dict) -> Any:
        """Executa uma tarefa individual"""
        # Implementação específica para cada tipo de tarefa
        task_type = task.get('type')
        if task_type == 'system_design':
            return await self._execute_system_design_task(task)
        elif task_type == 'code_generation':
            return await self._execute_code_generation_task(task)
        else:
            raise ValueError(f"Tipo de tarefa desconhecido: {task_type}")

    def to_dict(self) -> Dict:
        """Converte o workflow para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'tasks': self.tasks,
            'current_task_index': self.current_task_index,
            'results': self.results,
            'errors': self.errors,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'config': self.config
        }