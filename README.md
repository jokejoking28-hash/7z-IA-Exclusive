# 7z IA Exclusive - Agente Autônomo Gemini (Protótipo)

Este projeto é um protótipo de um Agente de Inteligência Artificial Autônomo, inspirado no Manus, que utiliza a API Gemini para planejar e executar tarefas complexas. Ele é implementado como uma API Web usando **FastAPI** para receber tarefas via webhook e processá-las de forma assíncrona.

## Funcionalidades Principais

*   **Planejamento Autônomo:** Transforma uma descrição de tarefa complexa em um plano sequencial de passos.
*   **Execução de Fluxo de Trabalho:** Executa cada passo do plano, despachando para ferramentas simuladas (`code_generator`, `content_generator`, `web_scraper`, `data_analyzer`).
*   **API Web (Webhook):** Recebe tarefas via `POST` e responde imediatamente, processando a tarefa em segundo plano.
*   **Operação Assíncrona:** Utiliza `BackgroundTasks` do FastAPI para garantir que o processamento da IA não bloqueie a API.

## Estrutura do Projeto

```
7z_ia_exclusive/
├── api.py              # Aplicação FastAPI e endpoint de webhook
├── agent.py            # Classe principal do Agente Autônomo (planejamento e execução)
├── tools.py            # Funções que simulam as ferramentas (Geração de Código, Conteúdo, etc.)
├── requirements.txt    # Dependências do Python
└── README.md           # Este arquivo
```

## Configuração e Deploy no Ubuntu Server

Siga os passos abaixo para configurar e rodar a API no seu servidor Ubuntu.

### 1. Pré-requisitos

*   Servidor Ubuntu (Server ou Desktop)
*   Python 3.8+
*   Conta no GitHub para clonar o repositório.

### 2. Clonar o Repositório

No seu servidor Ubuntu, instale o `git` se necessário e clone o repositório:

```bash
sudo apt update
sudo apt install git -y
git clone https://github.com/jokejoking28-hash/7z-IA-Exclusive.git
cd 7z-IA-Exclusive
```

### 3. Configurar o Ambiente Python

Crie e ative um ambiente virtual para isolar as dependências:

```bash
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configurar a Chave de API do Gemini

A aplicação requer a sua chave de API do Gemini para funcionar. **NUNCA** coloque a chave diretamente no código. Use variáveis de ambiente.

```bash
# Substitua 'SUA_CHAVE_AQUI' pela sua chave real do Gemini
export GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

> **Dica:** Para que a chave persista após o reboot, adicione a linha `export GEMINI_API_KEY="SUA_CHAVE_AQUI"` ao final do arquivo `~/.bashrc` ou `~/.profile`.

### 5. Rodar a API

Use o `uvicorn` para iniciar o servidor web.

```bash
# Certifique-se de que o ambiente virtual está ativo: source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000
```

A API estará acessível em `http://SEU_IP_DO_SERVIDOR:8000`.

### 6. Uso do Webhook

Para enviar uma tarefa, envie uma requisição `POST` para o endpoint `/webhook`.

**URL:** `http://SEU_IP_DO_SERVIDOR:8000/webhook`

**Método:** `POST`

**Corpo da Requisição (JSON):**

```json
{
  "task_description": "Criar um script Python que faça uma pesquisa na web sobre as 3 principais notícias de IA de hoje, gere um resumo de 5 linhas para cada uma e salve o resultado em um arquivo Markdown.",
  "callback_url": "http://SEU_SITE_DE_CHAT/api/callback"
}
```

A API responderá imediatamente com `{"status": "processing", ...}` e o agente começará a trabalhar em segundo plano. O resultado final será enviado para a `callback_url` fornecida.

## Próximos Passos (Desenvolvimento)

Este é um protótipo. Para torná-lo um produto completo, as seguintes melhorias são sugeridas:

1.  **Ferramentas Reais:** Substituir as funções simuladas em `tools.py` por implementações reais (ex: `requests` para web scraping, `subprocess` para execução de código gerado).
2.  **Gerenciamento de Estado:** Implementar um banco de dados (ex: SQLite ou PostgreSQL) para persistir o estado das tarefas e permitir que o usuário consulte o progresso.
3.  **Segurança:** Adicionar autenticação e validação de webhook.
4.  **Assincronicidade Completa:** Migrar o `google-genai` para um cliente assíncrono (se disponível) ou usar bibliotecas como `anyio` para gerenciar o `asyncio.to_thread` de forma mais robusta.
