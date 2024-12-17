# workflows/process_orchestrator.py
from typing import Dict, List, Any, Optional
from enum import Enum
import asyncio
from datetime import datetime
import logging
from pathlib import Path

class ProcessStatus(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessOrchestrator:
    def __init__(self, workflow_manager, task_scheduler):
        self.workflow_manager = workflow_manager
        self.task_scheduler = task_scheduler
        self.active_processes: Dict[str, Dict] = {}
        self.process_dependencies: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(__name__)

    async def create_process(self, process_config: Dict) -> str:
        """Cria um novo processo com suas dependências"""
        process_id = process_config['id']
        self.active_processes[process_id] = {
            'config': process_config,
            'status': ProcessStatus.INITIALIZING,
            'start_time': None,
            'end_time': None,
            'current_step': None,
            'results': {},
            'errors': []
        }
        
        # Configura dependências
        if 'dependencies' in process_config:
            self.process_dependencies[process_id] = process_config['dependencies']

        return process_id

    async def start_process(self, process_id: str) -> None:
        """Inicia a execução de um processo"""
        if process_id not in self.active_processes:
            raise ValueError(f"Processo {process_id} não encontrado")

        process = self.active_processes[process_id]
        if not await self._check_dependencies(process_id):
            process['status'] = ProcessStatus.WAITING
            return

        process['status'] = ProcessStatus.RUNNING
        process['start_time'] = datetime.now()

        try:
            await self._execute_process_steps(process_id)
        except Exception as e:
            process['status'] = ProcessStatus.FAILED
            process['errors'].append({
                'time': datetime.now().isoformat(),
                'error': str(e)
            })
            self.logger.error(f"Erro no processo {process_id}: {str(e)}")

    async def _check_dependencies(self, process_id: str) -> bool:
        """Verifica se todas as dependências foram satisfeitas"""
        if process_id not in self.process_dependencies:
            return True

        for dep_id in self.process_dependencies[process_id]:
            if dep_id not in self.active_processes:
                return False
            if self.active_processes[dep_id]['status'] != ProcessStatus.COMPLETED:
                return False

        return True

    async def _execute_process_steps(self, process_id: str) -> None:
        """Executa os passos de um processo"""
        process = self.active_processes[process_id]
        steps = process['config'].get('steps', [])

        for step in steps:
            process['current_step'] = step['id']
            
            try:
                if step['type'] == 'workflow':
                    result = await self._execute_workflow_step(step)
                elif step['type'] == 'task':
                    result = await self._execute_task_step(step)
                else:
                    raise ValueError(f"Tipo de passo desconhecido: {step['type']}")

                process['results'][step['id']] = result

            except Exception as e:
                process['errors'].append({
                    'step_id': step['id'],
                    'error': str(e),
                    'time': datetime.now().isoformat()
                })
                if not process['config'].get('continue_on_error', False):
                    raise

        process['status'] = ProcessStatus.COMPLETED
        process['end_time'] = datetime.now()
        await self._check_dependent_processes(process_id)

    async def _execute_workflow_step(self, step: Dict) -> Any:
        """Executa um passo do tipo workflow"""
        workflow_id = await self.workflow_manager.create_workflow(
            step['name'],
            step['tasks'],
            step.get('config', {})
        )
        await self.workflow_manager.start_workflow

        # Continuação do workflows/process_orchestrator.py
    async def _execute_workflow_step(self, step: Dict) -> Any:
        """Executa um passo do tipo workflow"""
        workflow_id = await self.workflow_manager.create_workflow(
            step['name'],
            step['tasks'],
            step.get('config', {})
        )
        await self.workflow_manager.start_workflow(workflow_id)
        
        # Aguarda a conclusão do workflow
        while True:
            status = self.workflow_manager.get_workflow_status(workflow_id)
            if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                break
            await asyncio.sleep(1)
        
        workflow = self.workflow_manager.workflows[workflow_id]
        return workflow.results

    async def _execute_task_step(self, step: Dict) -> Any:
        """Executa um passo do tipo task"""
        await self.task_scheduler.schedule_task(
            task_id=step['id'],
            task_data=step['task_data'],
            scheduled_time=datetime.now(),
            priority=step.get('priority', 0)
        )
        
        # Aguarda a conclusão da tarefa
        while step['id'] in self.task_scheduler.get_running_tasks():
            await asyncio.sleep(1)
            
        return self.task_scheduler.get_task_result(step['id'])

    async def _check_dependent_processes(self, completed_process_id: str) -> None:
        """Verifica e inicia processos dependentes"""
        for process_id, dependencies in self.process_dependencies.items():
            if completed_process_id in dependencies:
                if await self._check_dependencies(process_id):
                    process = self.active_processes[process_id]
                    if process['status'] == ProcessStatus.WAITING:
                        await self.start_process(process_id)

    def get_process_status(self, process_id: str) -> Optional[ProcessStatus]:
        """Retorna o status de um processo"""
        if process_id in self.active_processes:
            return self.active_processes[process_id]['status']
        return None

    def get_process_results(self, process_id: str) -> Dict:
        """Retorna os resultados de um processo"""
        if process_id in self.active_processes:
            return self.active_processes[process_id]['results']
        return {}

    def get_process_errors(self, process_id: str) -> List[Dict]:
        """Retorna os erros de um processo"""
        if process_id in self.active_processes:
            return self.active_processes[process_id]['errors']
        return []