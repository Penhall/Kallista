# workflows/task_scheduler.py
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import heapq
from dataclasses import dataclass, field
import logging

@dataclass(order=True)
class ScheduledTask:
    scheduled_time: datetime
    task_id: str = field(compare=False)
    task_data: Dict = field(compare=False)
    priority: int = field(compare=False)
    recurring: bool = field(compare=False)
    interval: Optional[timedelta] = field(compare=False)

class TaskScheduler:
    def __init__(self):
        self.task_queue: List[ScheduledTask] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(__name__)

    async def schedule_task(self, task_id: str, task_data: Dict, 
                          scheduled_time: datetime, priority: int = 0,
                          recurring: bool = False, 
                          interval: Optional[timedelta] = None) -> None:
        """Agenda uma nova tarefa"""
        task = ScheduledTask(
            scheduled_time=scheduled_time,
            task_id=task_id,
            task_data=task_data,
            priority=priority,
            recurring=recurring,
            interval=interval
        )
        heapq.heappush(self.task_queue, task)
        self.logger.info(f"Tarefa {task_id} agendada para {scheduled_time}")

    async def start(self) -> None:
        """Inicia o scheduler"""
        while True:
            await self._process_next_task()
            await asyncio.sleep(1)  # Previne uso excessivo de CPU

    async def _process_next_task(self) -> None:
        """Processa a próxima tarefa na fila"""
        if not self.task_queue:
            return

        now = datetime.now()
        next_task = self.task_queue[0]  # Peek sem remover

        if next_task.scheduled_time <= now:
            task = heapq.heappop(self.task_queue)
            await self._execute_task(task)

            # Reagenda se for uma tarefa recorrente
            if task.recurring and task.interval:
                next_time = task.scheduled_time + task.interval
                await self.schedule_task(
                    task.task_id,
                    task.task_data,
                    next_time,
                    task.priority,
                    task.recurring,
                    task.interval
                )

    async def _execute_task(self, task: ScheduledTask) -> None:
        """Executa uma tarefa agendada"""
        try:
            # Cria uma task asyncio para execução assíncrona
            running_task = asyncio.create_task(
                self._run_task(task)
            )
            self.running_tasks[task.task_id] = running_task
            await running_task
        except Exception as e:
            self.logger.error(f"Erro ao executar tarefa {task.task_id}: {str(e)}")
        finally:
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]

    async def _run_task(self, task: ScheduledTask) -> None:
        """Executa a lógica específica da tarefa"""
        self.logger.info(f"Executando tarefa {task.task_id}")
        # Implementação específica para cada tipo de tarefa
        task_type = task.task_data.get('type')
        if task_type == 'system_design':
            await self._run_system_design_task(task)
        elif task_type == 'code_generation':
            await self._run_code_generation_task(task)
        else:
            raise ValueError(f"Tipo de tarefa desconhecido: {task_type}")

    async def cancel_task(self, task_id: str) -> bool:
        """Cancela uma tarefa agendada"""
        # Cancela se estiver em execução
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
            return True

        # Remove da fila se ainda não começou
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                self.task_queue.pop(i)
                heapq.heapify(self.task_queue)
                return True

        return False

    def get_scheduled_tasks(self) -> List[Dict]:
        """Retorna todas as tarefas agendadas"""
        return [
            {
                'task_id': task.task_id,
                'scheduled_time': task.scheduled_time.isoformat(),
                'priority': task.priority,
                'recurring': task.recurring,
                'interval': str(task.interval) if task.interval else None,
                'task_data': task.task_data
            }
            for task in self.task_queue
        ]

    def get_running_tasks(self) -> List[str]:
        """Retorna IDs das tarefas em execução"""
        return list(self.running_tasks.keys())