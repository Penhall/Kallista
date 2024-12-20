# tests/integration/test_workflow_integration.py
import unittest
import asyncio
from pathlib import Path
import json
from datetime import datetime

from workflows.workflow_manager import WorkflowManager
from workflows.task_scheduler import TaskScheduler
from workflows.process_orchestrator import ProcessOrchestrator
from core.management.state_manager import StateManager
from core.management.context_manager import ContextManager
from agents.specialized.wpf_agent import WPFAgent
from agents.specialized.database_agent import DatabaseAgent

class TestWorkflowIntegration(unittest.TestCase):
    def setUp(self):
        """Setup para os testes de integração de workflows"""
        # Configurações
        self.config = {
            'state_file': 'test_state.json',
            'context_file': 'test_context.json',
            'workflow_file': 'test_workflow.json',
            'persist_state': True
        }
        
        # Inicializa componentes
        self.state_manager = StateManager(self.config)
        self.context_manager = ContextManager(self.config)
        
        # Inicializa gerenciadores de workflow
        self.workflow_manager = WorkflowManager(
            state_manager=self.state_manager,
            context_manager=self.context_manager
        )
        
        self.task_scheduler = TaskScheduler(
            state_manager=self.state_manager,
            context_manager=self.context_manager
        )
        
        self.process_orchestrator = ProcessOrchestrator(
            state_manager=self.state_manager,
            context_manager=self.context_manager
        )
        
        # Inicializa agentes
        self.wpf_agent = WPFAgent(
            state_manager=self.state_manager,
            context_manager=self.context_manager
        )
        
        self.database_agent = DatabaseAgent(
            state_manager=self.state_manager,
            context_manager=self.context_manager
        )

    def tearDown(self):
        """Limpeza após os testes"""
        test_files = [
            'test_state.json',
            'test_context.json',
            'test_workflow.json'
        ]
        
        for file in test_files:
            path = Path(file)
            if path.exists():
                path.unlink()

    async def test_wpf_project_workflow(self):
        """Testa workflow de criação de projeto WPF"""
        # Configuração do workflow
        workflow_config = {
            'name': 'create_wpf_project',
            'steps': [
                {
                    'name': 'setup_project',
                    'type': 'project_setup',
                    'config': {
                        'name': 'TestWPFApp',
                        'template': 'wpf_mvvm'
                    }
                },
                {
                    'name': 'create_ui',
                    'type': 'ui_generation',
                    'config': {
                        'components': ['main_window', 'login_form']
                    }
                },
                {
                    'name': 'setup_database',
                    'type': 'database_setup',
                    'config': {
                        'type': 'sql_server',
                        'entities': ['users', 'products']
                    }
                }
            ]
        }
        
        # 1. Cria e inicia workflow
        workflow_id = await self.workflow_manager.create_workflow(workflow_config)
        await self.workflow_manager.start_workflow(workflow_id)
        
        # 2. Aguarda conclusão
        result = await self.workflow_manager.wait_for_completion(workflow_id)
        
        # Verifica resultado
        self.assertEqual(result['status'], 'completed')
        self.assertTrue(result['success'])
        self.assertIn('project_path', result['output'])
        
        # Verifica artefatos gerados
        project_path = Path(result['output']['project_path'])
        self.assertTrue(project_path.exists())
        self.assertTrue((project_path / 'MainWindow.xaml').exists())
        self.assertTrue((project_path / 'App.config').exists())

    async def test_task_scheduling(self):
        """Testa agendamento e execução de tarefas"""
        # Prepara tarefas
        tasks = [
            {
                'name': 'generate_view',
                'type': 'ui_generation',
                'config': {
                    'component': 'user_form',
                    'style': 'modern'
                },
                'priority': 'high'
            },
            {
                'name': 'generate_viewmodel',
                'type': 'code_generation',
                'config': {
                    'component': 'user_form',
                    'pattern': 'mvvm'
                },
                'priority': 'medium'
            },
            {
                'name': 'generate_model',
                'type': 'code_generation',
                'config': {
                    'component': 'user',
                    'type': 'entity'
                },
                'priority': 'low'
            }
        ]
        
        # 1. Agenda tarefas
        task_ids = []
        for task in tasks:
            task_id = await self.task_scheduler.schedule_task(task)
            task_ids.append(task_id)
        
        # 2. Executa tarefas
        results = await self.task_scheduler.execute_tasks()
        
        # Verifica resultados
        self.assertEqual(len(results), len(tasks))
        self.assertTrue(all(r['success'] for r in results))
        
        # Verifica ordem de execução (por prioridade)
        execution_order = [r['task']['priority'] for r in results]
        self.assertEqual(
            execution_order,
            ['high', 'medium', 'low']
        )

    async def test_process_orchestration(self):
        """Testa orquestração de processos"""
        # Define processo
        process_config = {
            'name': 'setup_full_project',
            'steps': [
                {
                    'id': 'setup_solution',
                    'type': 'project_setup',
                    'config': {'name': 'TestSolution'}
                },
                {
                    'id': 'setup_ui_project',
                    'type': 'wpf_project',
                    'config': {'name': 'UI'},
                   # tests/integration/test_workflow_integration.py (continuação)
                    'dependencies': ['setup_solution']
                },
                {
                    'id': 'setup_data_project',
                    'type': 'database_project',
                    'config': {'name': 'Data'},
                    'dependencies': ['setup_solution']
                },
                {
                    'id': 'setup_test_project',
                    'type': 'test_project',
                    'config': {'name': 'Tests'},
                    'dependencies': ['setup_ui_project', 'setup_data_project']
                }
            ],
            'output_dir': 'test_output'
        }
        
        # 1. Inicia processo
        process_id = await self.process_orchestrator.create_process(process_config)
        await self.process_orchestrator.start_process(process_id)
        
        # 2. Aguarda conclusão
        result = await self.process_orchestrator.wait_for_completion(process_id)
        
        # Verifica resultado
        self.assertEqual(result['status'], 'completed')
        self.assertTrue(result['success'])
        
        # Verifica ordem de execução
        execution_order = [
            step['id'] for step in result['steps_executed']
        ]
        self.assertEqual(execution_order[0], 'setup_solution')
        self.assertTrue(
            execution_order.index('setup_test_project') >
            execution_order.index('setup_ui_project')
        )
        
        # Verifica estrutura gerada
        output_dir = Path(process_config['output_dir'])
        self.assertTrue(output_dir.exists())
        self.assertTrue((output_dir / 'TestSolution.sln').exists())
        self.assertTrue((output_dir / 'UI').exists())
        self.assertTrue((output_dir / 'Data').exists())
        self.assertTrue((output_dir / 'Tests').exists())

    async def test_workflow_error_handling(self):
        """Testa tratamento de erros em workflows"""
        # Workflow com erro
        workflow_config = {
            'name': 'error_test_workflow',
            'steps': [
                {
                    'name': 'valid_step',
                    'type': 'project_setup',
                    'config': {'name': 'TestProject'}
                },
                {
                    'name': 'error_step',
                    'type': 'invalid_type',
                    'config': {}
                },
                {
                    'name': 'recovery_step',
                    'type': 'cleanup',
                    'config': {},
                    'error_handler': True
                }
            ]
        }
        
        # 1. Executa workflow
        workflow_id = await self.workflow_manager.create_workflow(workflow_config)
        await self.workflow_manager.start_workflow(workflow_id)
        
        result = await self.workflow_manager.wait_for_completion(workflow_id)
        
        # Verifica tratamento de erro
        self.assertEqual(result['status'], 'completed_with_errors')
        self.assertTrue(result['recovery_executed'])
        self.assertEqual(len(result['errors']), 1)
        
        # Verifica execução do error handler
        self.assertIn('recovery_step', [
            step['name'] for step in result['steps_executed']
        ])

    async def test_workflow_recovery(self):
        """Testa recuperação de workflow após falha"""
        workflow_config = {
            'name': 'recovery_test_workflow',
            'steps': [
                {
                    'name': 'step1',
                    'type': 'setup',
                    'config': {'data': 'test1'}
                },
                {
                    'name': 'step2',
                    'type': 'process',
                    'config': {'data': 'test2'}
                }
            ],
            'recovery_point': True
        }
        
        # 1. Inicia workflow
        workflow_id = await self.workflow_manager.create_workflow(workflow_config)
        await self.workflow_manager.start_workflow(workflow_id)
        
        # 2. Simula falha
        await self.workflow_manager.simulate_failure(workflow_id)
        
        # 3. Recupera workflow
        recovered = await self.workflow_manager.recover_workflow(workflow_id)
        
        # Verifica recuperação
        self.assertTrue(recovered['success'])
        self.assertEqual(recovered['status'], 'resumed')
        self.assertTrue(recovered['data_preserved'])

    async def test_parallel_workflow_execution(self):
        """Testa execução paralela de workflows"""
        # Prepara múltiplos workflows
        workflow_configs = [
            {
                'name': f'parallel_workflow_{i}',
                'steps': [
                    {
                        'name': 'setup',
                        'type': 'project_setup',
                        'config': {'name': f'Project_{i}'}
                    },
                    {
                        'name': 'build',
                        'type': 'build',
                        'config': {}
                    }
                ]
            } for i in range(3)
        ]
        
        # 1. Inicia workflows em paralelo
        workflow_ids = []
        for config in workflow_configs:
            workflow_id = await self.workflow_manager.create_workflow(config)
            workflow_ids.append(workflow_id)
        
        # 2. Executa em paralelo
        tasks = [
            self.workflow_manager.start_workflow(wid)
            for wid in workflow_ids
        ]
        results = await asyncio.gather(*tasks)
        
        # Verifica resultados
        self.assertEqual(len(results), len(workflow_configs))
        self.assertTrue(all(r['success'] for r in results))
        
        # Verifica execução paralela
        execution_times = [
            r['completion_time'] - r['start_time']
            for r in results
        ]
        max_sequential_time = sum(execution_times)
        total_time = max(execution_times)
        self.assertLess(total_time, max_sequential_time)

    async def test_workflow_monitoring(self):
        """Testa monitoramento de workflows"""
        # Inicia workflow longo
        workflow_config = {
            'name': 'monitored_workflow',
            'steps': [
                {
                    'name': 'long_step',
                    'type': 'processing',
                    'config': {'duration': 2}  # 2 segundos
                }
            ]
        }
        
        workflow_id = await self.workflow_manager.create_workflow(workflow_config)
        await self.workflow_manager.start_workflow(workflow_id)
        
        # Monitora progresso
        progress_updates = []
        
        async def monitor_progress():
            while True:
                status = await self.workflow_manager.get_workflow_status(workflow_id)
                progress_updates.append(status)
                if status['status'] in ['completed', 'failed']:
                    break
                await asyncio.sleep(0.5)
        
        # Executa monitoramento
        await monitor_progress()
        
        # Verifica atualizações
        self.assertTrue(len(progress_updates) > 1)
        self.assertEqual(progress_updates[-1]['status'], 'completed')
        self.assertTrue(
            progress_updates[-1]['progress'] >
            progress_updates[0]['progress']
        )

if __name__ == '__main__':
    unittest.main()