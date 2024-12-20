# 📘 Kallista - Referência da API

## 🔍 Visão Geral

A API do Kallista é organizada em módulos principais que fornecem funcionalidades específicas para cada aspecto do desenvolvimento de software. Esta documentação detalha todas as classes, métodos e parâmetros disponíveis.

## 📚 Core API

### StateManager
```python
class StateManager:
    """Gerencia o estado global do sistema."""
    
    async def get_state(key: str) -> Any:
        """
        Recupera um valor do estado.
        
        Args:
            key (str): Chave do estado
            
        Returns:
            Any: Valor armazenado
            
        Raises:
            KeyError: Se a chave não existir
        """
        
    async def set_state(key: str, value: Any) -> None:
        """
        Define um valor no estado.
        
        Args:
            key (str): Chave do estado
            value (Any): Valor a ser armazenado
            
        Raises:
            ValueError: Se o valor for inválido
        """
```

### MemoryManager
```python
class MemoryManager:
    """Gerencia memória de curto e longo prazo."""
    
    async def store_short_term(key: str, value: Any) -> None:
        """
        Armazena valor na memória de curto prazo.
        
        Args:
            key (str): Chave da memória
            value (Any): Valor a ser armazenado
        """
        
    async def store_long_term(key: str, value: Any) -> None:
        """
        Armazena valor na memória de longo prazo.
        
        Args:
            key (str): Chave da memória
            value (Any): Valor a ser armazenado
        """
        
    async def retrieve(key: str) -> Optional[Any]:
        """
        Recupera valor da memória.
        
        Args:
            key (str): Chave da memória
            
        Returns:
            Optional[Any]: Valor armazenado ou None
        """
```

## 🤖 Agents API

### ArchitectAgent
```python
class ArchitectAgent:
    """Agente responsável por decisões arquiteturais."""
    
    async def design_system(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria design do sistema baseado em requisitos.
        
        Args:
            config (Dict[str, Any]): Configuração do sistema
            
        Returns:
            Dict[str, Any]: Design do sistema
        """
        
    async def validate_design(design: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Valida um design de sistema.
        
        Args:
            design (Dict[str, Any]): Design a ser validado
            
        Returns:
            List[Dict[str, Any]]: Lista de validações
        """
```

### WPFAgent
```python
class WPFAgent:
    """Agente especializado em desenvolvimento WPF."""
    
    async def design_interface(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria design de interface WPF.
        
        Args:
            config (Dict[str, Any]): Configuração da interface
            
        Returns:
            Dict[str, Any]: Design da interface
        """
        
    async def generate_xaml(design: Dict[str, Any]) -> str:
        """
        Gera código XAML baseado no design.
        
        Args:
            design (Dict[str, Any]): Design da interface
            
        Returns:
            str: Código XAML gerado
        """
```

## 🛠️ Tools API

### CodeGenerator
```python
class CodeGenerator:
    """Gerador de código baseado em templates."""
    
    async def generate_code(
        template: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Gera código usando template.
        
        Args:
            template (str): Nome do template
            params (Dict[str, Any]): Parâmetros
            
        Returns:
            str: Código gerado
            
        Raises:
            TemplateNotFoundError: Se template não existir
            ValidationError: Se parâmetros forem inválidos
        """
```

### SecurityScanner
```python
class SecurityScanner:
    """Scanner de segurança de código."""
    
    async def scan_code(
        path: Path,
        rules: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analisa código em busca de vulnerabilidades.
        
        Args:
            path (Path): Caminho do código
            rules (List[Dict[str, Any]], optional): Regras customizadas
            
        Returns:
            List[Dict[str, Any]]: Vulnerabilidades encontradas
        """
```

## 🔄 Workflows API

### WorkflowManager
```python
class WorkflowManager:
    """Gerenciador de workflows."""
    
    async def create_workflow(
        name: str,
        steps: List[Dict[str, Any]],
        config: Dict[str, Any] = None
    ) -> str:
        """
        Cria novo workflow.
        
        Args:
            name (str): Nome do workflow
            steps (List[Dict[str, Any]]): Passos do workflow
            config (Dict[str, Any], optional): Configurações
            
        Returns:
            str: ID do workflow
        """
        
    async def execute_workflow(
        workflow_id: str,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Executa um workflow.
        
        Args:
            workflow_id (str): ID do workflow
            params (Dict[str, Any], optional): Parâmetros
            
        Returns:
            Dict[str, Any]: Resultado da execução
        """
```

## 🔌 Integrations API

### VSIntegration
```python
class VSIntegration:
    """Integração com Visual Studio."""
    
    async def setup_project(
        project_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configura projeto no Visual Studio.
        
        Args:
            project_config (Dict[str, Any]): Configuração
            
        Returns:
            Dict[str, Any]: Status da configuração
        """
```

### GitHubIntegration
```python
class GitHubIntegration:
    """Integração com GitHub."""
    
    async def create_pull_request(
        pr_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria Pull Request.
        
        Args:
            pr_config (Dict[str, Any]): Configuração do PR
            
        Returns:
            Dict[str, Any]: Detalhes do PR criado
        """
```

## 📊 Performance API

### CacheManager
```python
class CacheManager:
    """Gerenciador de cache."""
    
    async def get(key: str) -> Optional[Any]:
        """
        Recupera item do cache.
        
        Args:
            key (str): Chave do item
            
        Returns:
            Optional[Any]: Valor ou None
        """
        
    async def set(
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Adiciona item ao cache.
        
        Args:
            key (str): Chave do item
            value (Any): Valor
            ttl (Optional[int]): Tempo de vida em segundos
            
        Returns:
            bool: Sucesso da operação
        """
```

## 🔒 Security API

### SecurityManager
```python
class SecurityManager:
    """Gerenciador de segurança."""
    
    async def analyze_security(
        project_path: Path
    ) -> Dict[str, Any]:
        """
        Realiza análise de segurança.
        
        Args:
            project_path (Path): Caminho do projeto
            
        Returns:
            Dict[str, Any]: Resultados da análise
        """
        
    async def check_compliance(
        project_path: Path,
        standards: List[str] = None
    ) -> Dict[str, Any]:
        """
        Verifica compliance.
        
        Args:
            project_path (Path): Caminho do projeto
            standards (List[str], optional): Padrões
            
        Returns:
            Dict[str, Any]: Resultados da verificação
        """
```

## 📋 Parâmetros Comuns

### ProjectConfig
```python
ProjectConfig = Dict[str, Any]
"""
Configuração de projeto.

Keys:
    name (str): Nome do projeto
    type (str): Tipo do projeto ('WPF', 'Library', etc)
    template (str): Template base
    features (List[str]): Features a serem incluídas
    settings (Dict[str, Any]): Configurações específicas
"""
```

### WorkflowStep
```python
WorkflowStep = Dict[str, Any]
"""
Passo de workflow.

Keys:
    type (str): Tipo do passo
    config (Dict[str, Any]): Configuração do passo
    dependencies (List[str]): Dependências
    timeout (int): Timeout em segundos
    retry (Dict[str, Any]): Configuração de retry
"""
```

## ⚠️ Exceções

```python
class KallistaError(Exception):
    """Exceção base do Kallista."""
    pass

class ValidationError(KallistaError):
    """Erro de validação."""
    pass

class ConfigurationError(KallistaError):
    """Erro de configuração."""
    pass

class IntegrationError(KallistaError):
    """Erro de integração."""
    pass

class WorkflowError(KallistaError):
    """Erro em workflow."""
    pass
```

---
Data de Atualização: 19/12/2024