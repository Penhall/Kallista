# cli/command_handler.py
import json
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from .spec_converter import SpecificationConverter
from .agent_integration import AgentIntegrator

class ProjectCLI:
    def __init__(self):
        # Comandos disponíveis
        self.commands = {
            'new': self.new_project,
            'help': self.show_help,
            'exit': self.exit_cli
        }
        
        # Tipos de projetos suportados
        self.project_types = [
            'dashboard', 
            'crud', 
            'kanban', 
            'report', 
            'document', 
            'custom'
        ]
        
        # Configurar autocompletion
        self.completer = WordCompleter(
            list(self.commands.keys()) + self.project_types
        ) 
        
        # Inicializar PromptSession        
        self.session = PromptSession(completer=self.completer)
        self.spec_converter = SpecificationConverter()
        self.agent_integrator = AgentIntegrator()

    def start(self):
        """Inicia o CLI interativo"""
        while True:
            try:
                command = self.session.prompt('Kallista> ').strip()
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Erro: {str(e)}")

    def process_command(self, command):
        """Processa o comando inserido"""
        cmd = command.split()[0].lower()
        args = command.split()[1:] if len(command.split()) > 1 else []
        
        if cmd in self.commands:
            if cmd == 'new':
                asyncio.run(self.new_project(args))
            else:
                self.commands[cmd](args)
        else:
            print(f"Comando desconhecido: {cmd}")


    async def new_project(self, args):
        """Inicia a criação de um novo projeto"""
        if not args:
            print("Uso: new <tipo_projeto>")
            print(f"Tipos disponíveis: {', '.join(self.project_types)}")
            return

        project_type = args[0].lower()
        if project_type not in self.project_types:
            print(f"Tipo inválido. Tipos disponíveis: {', '.join(self.project_types)}")
            return

        specs = self.collect_specs(project_type)
        await self.generate_structure(specs)

    def collect_specs(self, project_type):
        """Coleta as especificações do projeto"""
        specs = {
            'type': project_type,
            'name': input('Nome do projeto: '),
            'description': input('Descrição: '),
            'features': []
        }

        # Especificações específicas por tipo de projeto
        if project_type == 'dashboard':
            specs['data_source'] = input('Fonte de dados: ')
            specs['update_interval'] = input('Intervalo de atualização (s): ')
            specs['charts'] = input('Tipos de gráficos (separados por vírgula): ').split(',')
        
        elif project_type == 'crud':
            specs['entities'] = input('Entidades (separadas por vírgula): ').split(',')
            specs['relationships'] = input('Relacionamentos (opcional): ')

        elif project_type == 'kanban':
            specs['columns'] = input('Colunas do quadro (separadas por vírgula): ').split(',')
            specs['card_fields'] = input('Campos dos cartões (separados por vírgula): ').split(',')

        # Configurações comuns para todos os tipos
        specs['authentication'] = input('Requer autenticação? (s/n): ').lower() == 's'
        specs['database'] = input('Requer banco de dados? (s/n): ').lower() == 's'
        
        return specs

        """Gera a estrutura do projeto baseado nas especificações"""
        print("\nConvertendo especificações...")
        
        try:
            project_structure = self.spec_converter.convert_to_project_structure(specs)
            
            print("\nEstrutura do projeto gerada:")
            print(json.dumps(project_structure, indent=2))
            
            proceed = input("\nDeseja prosseguir com esta estrutura? (s/n): ")
            if proceed.lower() == 's':
                print("\nGerando projeto...")
                # TODO: Integrar com os agentes aqui
                print("Próximo passo: Integração com agentes")
            else:
                print("Geração cancelada")
                
        except Exception as e:
            print(f"Erro ao gerar estrutura: {str(e)}")
    
    async def generate_structure(self, specs):
        """Gera a estrutura do projeto baseado nas especificações"""
        print("\nConvertendo especificações...")
        
        try:
            project_structure = self.spec_converter.convert_to_project_structure(specs)
            
            print("\nEstrutura do projeto gerada:")
            print(json.dumps(project_structure, indent=2))
            
            proceed = input("\nDeseja prosseguir com esta estrutura? (s/n): ")
            if proceed.lower() == 's':
                print("\nGerando projeto...")
                result = await self.agent_integrator.generate_project(project_structure)
                print("\nResultado da geração:")
                print(result)
            else:
                print("Geração cancelada")
                
        except Exception as e:
            print(f"Erro ao gerar estrutura: {str(e)}")


    def show_help(self, args):
        """Mostra a ajuda do sistema"""
        print("\nComandos disponíveis:")
        print("  new <tipo>   - Criar novo projeto")
        print("  help         - Mostrar ajuda")
        print("  exit         - Sair")
        print("\nTipos de projeto disponíveis:")
        for t in self.project_types:
            print(f"  - {t}")

    def exit_cli(self, args):
        """Sai do sistema"""
        print("Encerrando...")
        raise EOFError