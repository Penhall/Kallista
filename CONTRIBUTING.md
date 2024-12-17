# 🤝 Guia de Contribuição

## Bem-vindo ao Kallista!

Primeiramente, obrigado por considerar contribuir para o Kallista! É pessoas como você que tornam o Kallista uma ferramenta incrível.

## 📝 Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Posso Contribuir?](#como-posso-contribuir)
3. [Reportando Bugs](#reportando-bugs)
4. [Sugerindo Melhorias](#sugerindo-melhorias)
5. [Processo de Pull Request](#processo-de-pull-request)
6. [Estilo de Código](#estilo-de-código)

## Código de Conduta

Este projeto e todos os participantes dele são governados pelo [Código de Conduta](CODE_OF_CONDUCT.md). Ao participar, você deve seguir este código.

## Como Posso Contribuir?

### 🐛 Reportando Bugs

- Use o template de issues para bugs
- Inclua o máximo de detalhes possível
- Inclua logs de erro se disponíveis
- Descreva os passos para reproduzir o problema

### 💡 Sugerindo Melhorias

- Use o template de issues para features
- Explique por que esta melhoria seria útil
- Inclua exemplos de uso quando possível
- Considere o impacto na base de código existente

## Processo de Pull Request

1. Fork do repositório
2. Clone seu fork (`git clone url-do-seu-fork`)
3. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
4. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. Push para a branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request

### Checklist do Pull Request

- [ ] Código segue o estilo do projeto
- [ ] Testes foram adicionados/atualizados
- [ ] Documentação foi atualizada
- [ ] Commit messages são claras e descritivas

## 🎨 Estilo de Código

### Python
- Siga o PEP 8
- Use type hints
- Docstrings em todas as funções/classes
- Mantenha funções pequenas e focadas

### C#
- Siga o C# Coding Conventions da Microsoft
- Use XML Documentation
- Implemente interfaces quando apropriado
- Mantenha o SOLID em mente

## 📚 Documentação

- Mantenha a documentação atualizada
- Use exemplos práticos
- Inclua docstrings e comentários apropriados
- Atualize o README.md quando necessário

## ⚙️ Configuração do Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/kallista.git

# Entre no diretório
cd kallista

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
source venv/bin/activate  # Linux/MacOS
.\venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Instale as dependências de desenvolvimento
pip install -r requirements-dev.txt
```

## 🧪 Testes

- Execute os testes antes de submeter um PR
- Adicione novos testes para novas features
- Mantenha a cobertura de testes alta

```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=kallista
```

## ❓ Dúvidas?

Sinta-se à vontade para abrir uma issue ou contactar os mantenedores:
- Reginaldo Santos - [penhall@gmail.com](mailto:penhall@gmail.com)

---
Agradecemos sua contribuição! 🙏
