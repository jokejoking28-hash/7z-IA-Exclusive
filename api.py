from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import asyncio
import os
import json

# Import the agent
from agent import AutonomousAgent

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
    task_id: str = None

# --- Background Task for Agent Execution ---

async def run_agent_task(task_description: str, callback_url: str):
    """
    Executes the autonomous agent's task and sends the result via callback.
    """
    # Check for API Key
    if "GEMINI_API_KEY" not in os.environ:
        final_result = "ERRO: GEMINI_API_KEY não configurada no ambiente do servidor."
    else:
        try:
            agent = AutonomousAgent()
            # Run the asynchronous agent's main loop
            final_result = await agent.run(task_description)
            
        except Exception as e:
            final_result = f"ERRO CRÍTICO durante a execução do agente: {e}"

    # --- Send Result via Callback (Simulation) ---
    if callback_url:
        print(f"Simulando envio do resultado para {callback_url}")
        print(f"Resultado: {final_result[:200]}...")
        # In a real application, you would use a library like 'httpx' to send a POST request
        # to the callback_url with the final_result.
        # Example:
        # async with httpx.AsyncClient() as client:
        #     await client.post(callback_url, json={"task_id": "...", "result": final_result})
    else:
        print("Tarefa concluída, mas sem URL de callback para envio do resultado.")
        print(f"Resultado final: {final_result}")

# --- API Endpoints ---

@app.post("/webhook", response_model=WebhookResponse)
async def handle_webhook(request: WebhookRequest, background_tasks: BackgroundTasks):
    """
    Receives a task via webhook and starts the autonomous agent in the background.
    """
    task_id = f"task-{os.urandom(4).hex()}" # Simple unique ID
    
    # Start the agent execution in a background task
    background_tasks.add_task(run_agent_task, request.task_description, request.callback_url)
    
    return WebhookResponse(
        status="processing",
        message=f"Tarefa '{request.task_description}' recebida e iniciada em segundo plano. O resultado será enviado para {request.callback_url} (se fornecido).",
        task_id=task_id
    )

@app.get("/")
async def root():
    return {"message": "7z IA Exclusive API está online. Use o endpoint /webhook para enviar tarefas."}

if __name__ == "__main__":
    import uvicorn
    # NOTE: This is for local testing. On a server, you would run:
    # uvicorn api:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
