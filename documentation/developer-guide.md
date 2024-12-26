# 📘 Kallista - Guia do Desenvolvedor

## 🎯 Visão Geral

O Kallista é estruturado em uma arquitetura modular baseada em agentes, utilizando o framework CrewAI como base. Este guia fornece as informações necessárias para desenvolvedores que desejam contribuir com o projeto.

## 🏗️ Arquitetura

### Core Components

```
kallista/
├── core/
│   ├── management/       # Gestão de estado e contexto
│   ├── communication/    # Comunicação entre agentes
│   └── logging/         # Sistema de logging
```

### Agentes Especializados

```
kallista/
├── agents/
│   ├── core/            # Agentes base do sistema
│   ├── specialized/     # Agentes específicos (WPF, DB, etc)
│   └── support/         # Agentes de suporte
```

### Ferramentas e Utilitários

```
kallista/
├── tools/
│   ├── code/           # Geradores e analisadores
│   ├── security/       # Ferramentas de segurança
│   └── performance/    # Otimização e monitoramento
```

## 🔧 Setup do Ambiente de Desenvolvimento

### 1. Requisitos
- Python 3.8+
- Visual Studio 2019+
- Git
- Docker (opcional)

### 2. Configuração
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/kallista.git
cd kallista

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Instale dependências de desenvolvimento
pip install -r requirements-dev.txt
```

### 3. Configurações de Desenvolvimento
```python
# config/development.py
DEVELOPMENT_CONFIG = {
    'DEBUG': True,
    'LOG_LEVEL': 'DEBUG',
    'MOCK_EXTERNAL_SERVICES': True,
    'USE_LOCAL_CACHE': True
}
```

## 🧪 Desenvolvimento e Testes

### Estrutura de Testes
```
tests/
├── unit/              # Testes unitários
├── integration/       # Testes de integração
└── performance/       # Testes de performance
```

### Executando Testes
```bash
# Testes unitários
python -m pytest tests/unit

# Testes de integração
python -m pytest tests/integration

# Testes de performance
python -m pytest tests/performance
```

### Code Coverage
```bash
# Gerar relatório de cobertura
coverage run -m pytest
coverage report
coverage html  # Gera relatório HTML
```

## 📝 Padrões de Código

### Estilo de Código
- PEP 8 para Python
- EditorConfig para padronização
- Black para formatação
- isort para imports

### Docstrings
```python
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa dados de entrada aplicando transformações.

    Args:
        data (Dict[str, Any]): Dados a serem processados

    Returns:
        Dict[str, Any]: Dados processados

    Raises:
        ValueError: Se os dados estiverem em formato inválido
    """
    pass
```

### Type Hints
```python
from typing import Dict, List, Optional, Union

def get_component(
    name: str,
    config: Optional[Dict[str, Any]] = None,
    features: List[str] = []
) -> Union[Component, None]:
    pass
```

## 🔄 Workflow de Desenvolvimento

### 1. Branches
- `main`: Branch principal
- `develop`: Branch de desenvolvimento
- `feature/*`: Features novas
- `bugfix/*`: Correções
- `release/*`: Preparação de releases

### 2. Commits
```bash
# Formato
<tipo>(<escopo>): <descrição>

# Exemplos
feat(core): adiciona novo sistema de cache
fix(agents): corrige memory leak no WPF agent
docs(api): atualiza documentação da API
```

### 3. Pull Requests
- Use o template fornecido
- Inclua testes
- Atualize documentação
- Siga checklist de review

## 🛠️ Ferramentas de Desenvolvimento

### VS Code Settings
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "files.trimTrailingWhitespace": true
}
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/psf/black
    rev: 21.9b0
    hooks:
    -   id: black
-   repo: https://github.com/pycqa/isort
    rev: 5.9.3
    hooks:
    -   id: isort
```

## 🔌 Integrações

### 1. Visual Studio
```python
from kallista.integrations.visual_studio import VSIntegration

vs_integration = VSIntegration()
await vs_integration.setup_project(project_config)
```

### 2. GitHub/Azure DevOps
```python
from kallista.integrations.github import GitHubIntegration
from kallista.integrations.azure import AzureDevOpsIntegration

# GitHub
github = GitHubIntegration(token=GITHUB_TOKEN)
await github.create_pull_request(pr_config)

# Azure DevOps
azure = AzureDevOpsIntegration(config=AZURE_CONFIG)
await azure.create_pipeline(pipeline_config)
```

## 🔒 Segurança

### 1. Análise de Segurança
```bash
# Executa análise de segurança
python -m kallista.tools.security.analyzer

# Scan de dependências
python -m kallista.tools.security.dependency_check
```

### 2. Compliance Check
```python
from kallista.tools.security import ComplianceChecker

checker = ComplianceChecker()
results = await checker.check_compliance(project_path)
```

## 📊 Monitoramento e Performance

### 1. Métricas
```python
from kallista.tools.performance import MetricsCollector

collector = MetricsCollector()
metrics = await collector.collect_metrics()
```

### 2. Profiling
```python
from kallista.tools.performance import Profiler

with Profiler() as p:
    # Código a ser analisado
    pass

p.print_stats()
```

## 📚 Recursos para Desenvolvedores

### Documentação Interna
- [Arquitetura Detalhada](docs/architecture.md)
- [Guia de API](docs/api-reference.md)
- [Padrões e Práticas](docs/patterns.md)

### Ferramentas
- [Scripts de Desenvolvimento](tools/dev/)
- [Utilitários de Build](tools/build/)
- [Ferramentas de Análise](tools/analysis/)

### Templates
- [Templates de Issue](.github/ISSUE_TEMPLATE/)
- [Templates de PR](.github/PULL_REQUEST_TEMPLATE/)
- [Templates de Código](templates/code/)

---
Data de Atualização: 19/12/2024