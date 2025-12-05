from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import asyncio
import os
import json
import uuid
import httpx

# Import the agent and database modules
from agent import AutonomousAgent
from db import init_db, create_task, update_task_status, get_task

# Initialize the database on startup
init_db()

app = FastAPI(title="7z IA Exclusive - Autonomous Agent API")

# --- Request/Response Schemas ---

class WebhookRequest(BaseModel):
    """Schema for the incoming webhook request."""
    task_description: str
    callback_url: str = None # URL to send the final result

class WebhookResponse(BaseModel):
    """Schema for the immediate response to the webhook."""
    status: str
    message: str
    task_id: str

# --- Helper Function for Callback ---

async def send_callback(task_id: str, callback_url: str, final_result: str):
    """Sends the final result to the callback URL."""
    print(f"Enviando resultado da tarefa {task_id} para {callback_url}")
    
    payload = {
        "task_id": task_id,
        "status": "COMPLETED",
        "result": final_result
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(callback_url, json=payload)
            response.raise_for_status()
            print(f"Callback enviado com sucesso. Status: {response.status_code}")
    except httpx.HTTPStatusError as e:
        print(f"Erro HTTP ao enviar callback: {e}")
    except httpx.RequestError as e:
        print(f"Erro de requisição ao enviar callback: {e}")
    except Exception as e:
        print(f"Erro desconhecido ao enviar callback: {e}")

# --- Background Task for Agent Execution ---

async def run_agent_task(task_id: str, task_description: str, callback_url: str):
    """
    Executes the autonomous agent's task, updates the DB, and sends the result via callback.
    """
    final_result = ""
    
    # Check for API Key
    if "GEMINI_API_KEY" not in os.environ:
        final_result = "ERRO: GEMINI_API_KEY não configurada no ambiente do servidor."
        update_task_status(task_id, "FAILED", final_result)
    else:
        try:
            # The agent now takes the task_id and a function to update the DB status
            agent = AutonomousAgent(task_id=task_id)
            final_result = await agent.run(task_description, update_task_status)
            
        except Exception as e:
            final_result = f"ERRO CRÍTICO durante a execução do agente: {e}"
            update_task_status(task_id, "FAILED", final_result)

    # Send Result via Callback
    if callback_url:
        await send_callback(task_id, callback_url, final_result)
    else:
        print(f"Tarefa {task_id} concluída, mas sem URL de callback para envio do resultado.")

# --- API Endpoints ---

@app.post("/webhook", response_model=WebhookResponse)
async def handle_webhook(request: WebhookRequest, background_tasks: BackgroundTasks):
    """
    Receives a task via webhook and starts the autonomous agent in the background.
    """
    task_id = str(uuid.uuid4()) # Generate a unique task ID
    
    # 1. Create task in DB with PENDING status
    create_task(task_id, request.task_description, request.callback_url)
    
    # 2. Start the agent execution in a background task
    background_tasks.add_task(run_agent_task, task_id, request.task_description, request.callback_url)
    
    return WebhookResponse(
        status="pending",
        message=f"Tarefa '{request.task_description}' recebida e iniciada em segundo plano. Acompanhe o status em /status/{task_id}.",
        task_id=task_id
    )

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Retrieves the current status and result of a task.
    """
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@app.get("/")
async def root():
    return {"message": "7z IA Exclusive API está online. Use o endpoint /webhook para enviar tarefas e /status/{task_id} para verificar o progresso."}

if __name__ == "__main__":
    import uvicorn
    # NOTE: This is for local testing. On a server, you would run:
    # uvicorn api:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
