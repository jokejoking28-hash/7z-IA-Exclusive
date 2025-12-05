# 7z IA Exclusive - Agente Autônomo Gemini (Protótipo Avançado)

Este projeto é um protótipo **avançado** de um Agente de Inteligência Artificial Autônomo, inspirado no Manus, que utiliza a API Gemini para planejar e executar tarefas complexas. Ele é implementado como uma API Web usando **FastAPI** para receber tarefas via webhook e processá-las de forma assíncrona.

## Novas Funcionalidades Avançadas

*   **Gerenciamento de Estado Persistente:** Utiliza **SQLite** (`tasks.db`) para rastrear o status (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`) e o resultado de cada tarefa.
*   **Ferramentas Reais:**
    *   **Web Scraper Real:** Implementado com `requests` e `BeautifulSoup` para coletar dados reais de notícias de IA.
    *   **Execução de Código Seguro:** Capacidade de gerar e executar código Python em um ambiente isolado (subprocesso com timeout) para automação.
*   **Comunicação Assíncrona Real:** Envio do resultado final via `POST` para a `callback_url` fornecida, usando `httpx`.
*   **Endpoint de Status:** Novo endpoint `/status/{task_id}` para verificar o progresso de uma tarefa.

## Estrutura do Projeto

```
7z_ia_exclusive/
├── api.py              # Aplicação FastAPI, endpoints de webhook e status
├── agent.py            # Classe principal do Agente Autônomo (planejamento e execução assíncrona)
├── tools.py            # Funções que implementam as ferramentas reais (Web Scraper, Execução de Código, etc.)
├── db.py               # Módulo para gerenciamento do banco de dados SQLite
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

### 5. Inicializar o Banco de Dados

O banco de dados SQLite será criado automaticamente na primeira execução da API, mas você pode inicializá-lo manualmente:

```bash
python3 db.py
```

### 6. Rodar a API

Use o `uvicorn` para iniciar o servidor web.

```bash
# Certifique-se de que o ambiente virtual está ativo: source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000
```

A API estará acessível em `http://SEU_IP_DO_SERVIDOR:8000`.

### 7. Uso da API

#### A. Enviar Tarefa (Webhook)

Para enviar uma tarefa, envie uma requisição `POST` para o endpoint `/webhook`.

**URL:** `http://SEU_IP_DO_SERVIDOR:8000/webhook`

**Método:** `POST`

**Corpo da Requisição (JSON):**

```json
{
  "task_description": "Crie um script Python que calcule o 5º número de Fibonacci e me diga o resultado.",
  "callback_url": "http://SEU_SITE_DE_CHAT/api/callback"
}
```

A API responderá imediatamente com `{"status": "pending", "task_id": "..."}`.

#### B. Verificar Status

Use o `task_id` retornado para verificar o progresso da tarefa.

**URL:** `http://SEU_IP_DO_SERVIDOR:8000/status/{task_id}`

**Método:** `GET`

O resultado final será enviado para a `callback_url` fornecida.

## Próximos Passos (Desenvolvimento)

Para um sistema de produção, as seguintes melhorias são sugeridas:

1.  **Orquestração de Agentes:** Implementar um sistema de agentes multi-agente (ex: usando LangChain ou CrewAI) para tarefas mais complexas.
2.  **Ferramentas de Busca:** Substituir o Web Scraper simples por uma ferramenta de busca mais robusta (ex: Google Search API).
3.  **Segurança:** Adicionar autenticação e validação de webhook mais robustas.
4.  **Monitoramento:** Implementar logs e métricas para monitorar a performance e o estado das tarefas.
