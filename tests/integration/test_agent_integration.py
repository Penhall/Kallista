# tests/integration/test_agent_integration.py
import unittest
import asyncio
from pathlib import Path
import json
from datetime import datetime

from agents.core.architect_agent import ArchitectAgent
from agents.specialized.wpf_agent import WPFAgent
from agents.specialized.database_agent import DatabaseAgent
from core.communication.agent_communicator import AgentCommunicator
from core.management.state_manager import StateManager
from core.management.context_manager import ContextManager
from core.management.memory_manager import MemoryManager

class TestAgentIntegration(unittest.TestCase):
    def setUp(self):
        """Setup para os testes de integração"""
        # Configurações
        self.config = {
            'state_file': 'test_state.json',
            'context_file': 'test_context.json',
            'memory_file': 'test_memory.json',
            'persist_state': True
        }
        
        # Inicializa componentes core
        self.state_manager = StateManager(self.config)
        self.context_manager = ContextManager(self.config)
        self.memory_manager = MemoryManager(self.config)
        self.communicator = AgentCommunicator(self.config)
        
        # Inicializa agentes
        self.architect_agent = ArchitectAgent(
            state_manager=self.state_manager,
            context_manager=self.context_manager,
            memory_manager=self.memory_manager,
            communicator=self.communicator
        )
        
        self.wpf_agent = WPFAgent(
            state_manager=self.state_manager,
            context_manager=self.context_manager,
            memory_manager=self.memory_manager,
            communicator=self.communicator
        )
        
        self.database_agent = DatabaseAgent(
            state_manager=self.state_manager,
            context_manager=self.context_manager,
            memory_manager=self.memory_manager,
            communicator=self.communicator
        )

    def tearDown(self):
        """Limpeza após os testes"""
        # Remove arquivos de teste
        test_files = [
            'test_state.json',
            'test_context.json',
            'test_memory.json'
        ]
        
        for file in test_files:
            path = Path(file)
            if path.exists():
                path.unlink()

    async def test_full_design_workflow(self):
        """Testa fluxo completo de design de sistema"""
        # Configuração do projeto
        project_config = {
            'name': 'TestProject',
            'type': 'WPF',
            'features': [
                'user_authentication',
                'data_persistence',
                'reporting'
            ]
        }
        
        # 1. Architect Agent inicia o design
        design_context = await self.architect_agent.start_design(project_config)
        
        # Verifica criação do contexto
        self.assertIsNotNone(design_context)
        self.assertEqual(design_context['status'], 'active')
        
        # 2. WPF Agent recebe e processa o design
        wpf_context = await self.wpf_agent.process_design(design_context['id'])
        
        # Verifica processamento do design
        self.assertIsNotNone(wpf_context)
        self.assertIn('ui_components', wpf_context['result'])
        
        # 3. Database Agent processa requisitos de dados
        db_context = await self.database_agent.process_requirements(
            design_context['id']
        )
        
        # Verifica processamento dos requisitos
        self.assertIsNotNone(db_context)
        self.assertIn('schema', db_context['result'])
        
        # 4. Architect Agent finaliza o design
        final_design = await self.architect_agent.finalize_design(
            design_context['id']
        )
        
        # Verifica design final
        self.assertEqual(final_design['status'], 'completed')
        self.assertIn('ui_design', final_design['result'])
        self.assertIn('data_design', final_design['result'])

    async def test_agent_communication(self):
        """Testa comunicação entre agentes"""
        # 1. Architect Agent envia mensagem para WPF Agent
        message_id = await self.architect_agent.request_ui_design({
            'component': 'login_form',
            'style': 'modern'
        })
        
        # Verifica envio da mensagem
        self.assertIsNotNone(message_id)
        
        # 2. WPF Agent processa a requisição
        response = await self.wpf_agent.process_messages()
        
        # Verifica processamento
        self.assertTrue(response['success'])
        self.assertIn('design', response['result'])
        
        # 3. Verifica estado compartilhado
        shared_state = await self.state_manager.get_state('current_design')
        self.assertIsNotNone(shared_state)
        self.assertIn('login_form', shared_state)

    async def test_concurrent_agent_operations(self):
        """Testa operações concorrentes entre agentes"""
        # Prepara requisições
        requests = [
            ('login_form', 'modern'),
            ('dashboard', 'minimal'),
            ('report_viewer', 'classic')
        ]
        
        async def request_design(component, style):
            # Envia requisição
            message_id = await self.architect_agent.request_ui_design({
                'component': component,
                'style': style
            })
            
            # Aguarda processamento
            await self.wpf_agent.process_messages()
            
            # Retorna resultado
            return await self.state_manager.get_state(f'design_{component}')
        
        # Executa requisições concorrentemente
        tasks = [
            request_design(component, style)
            for component, style in requests
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verifica resultados
        self.assertEqual(len(results), len(requests))
        for result in results:
            self.assertIsNotNone(result)
            self.assertIn('component', result)
            self.assertIn('design', result)

    async def test_agent_error_handling(self):
        """Testa tratamento de erros entre agentes"""
        # 1. Envia requisição inválida
        with self.assertRaises(ValueError):
            await self.architect_agent.request_ui_design({
                'component': None,
                'style': 'invalid'
            })
        
        # 2. Verifica log de erro
        error_state = await self.state_manager.get_state('error_log')
        self.assertIsNotNone(error_state)
        self.assertTrue(len(error_state) > 0)
        
        # 3. Verifica recuperação
        valid_request = await self.architect_agent.request_ui_design({
            'component': 'simple_form',
            'style': 'modern'
        })
        self.assertIsNotNone(valid_request)

    async def test_agent_memory_sharing(self):
        """Testa compartilhamento de memória entre agentes"""
        # 1. Architect Agent armazena design pattern
        pattern_data = {
            'name': 'MVVM',
            'components': ['view', 'viewmodel', 'model']
        }
        await self.architect_agent.store_design_pattern(pattern_data)
        
        # 2. WPF Agent acessa pattern
        retrieved_pattern = await self.wpf_agent.get_design_pattern('MVVM')
        
        # Verifica compartilhamento
        self.assertEqual(retrieved_pattern['name'], pattern_data['name'])
        self.assertEqual(
            retrieved_pattern['components'],
            pattern_data['components']
        )
        
        # 3. Verifica persistência
        new_wpf_agent = WPFAgent(
            state_manager=self.state_manager,
            context_manager=self.context_manager,
            memory_manager=self.memory_manager,
            communicator=self.communicator
        )
        
        persisted_pattern = await new_wpf_agent.get_design_pattern('MVVM')
        self.assertEqual(persisted_pattern, pattern_data)

if __name__ == '__main__':
    unittest.main()