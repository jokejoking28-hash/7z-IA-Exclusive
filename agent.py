import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
import asyncio
from tools import code_generator, content_generator, web_scraper, data_analyzer, execute_python_code

# --- Pydantic Schemas for Structured Output ---

class Step(BaseModel):
    """A single step in the overall plan."""
    step_id: int = Field(description="Unique identifier for the step, starting from 1.")
    description: str = Field(description="A clear, concise description of the action to be taken in this step.")
    tool_required: str = Field(description="The tool required for this step (e.g., 'code_generator', 'web_scraper', 'data_analyzer', or 'none').")

class Plan(BaseModel):
    """The complete plan for a complex task."""
    task_goal: str = Field(description="The overall goal of the task.")
    phases: List[Step] = Field(description="A sequential list of steps to achieve the task goal.")

# --- Autonomous Agent Class ---

class AutonomousAgent:
    """
    An autonomous agent that plans and executes complex tasks using the Gemini API.
    """
    def __init__(self, task_id: str, model_name: str = 'gemini-2.5-flash'):
        """Initializes the Gemini client."""
        # Assumes GEMINI_API_KEY is set in the environment
        self.client = genai.Client()
        self.model_name = model_name
        self.task_id = task_id
        self.history = [] # To maintain conversation history for context

    async def create_plan(self, task_description: str) -> Plan:
        """
        Generates a structured plan for a given task using the Gemini model.
        """
        print(f"-> Gerando plano para a tarefa: {task_description}")
        
        prompt = (
            f"Você é um planejador de tarefas autônomo. Sua função é transformar uma tarefa complexa em um plano sequencial de passos. "
            f"A tarefa é: '{task_description}'. "
            f"Crie um plano detalhado, identificando o objetivo principal e uma lista de fases (steps). "
            f"Para cada passo, indique a ferramenta necessária ('code_generator', 'web_scraper', 'data_analyzer', ou 'none')."
        )

        try:
            # Run the synchronous call in a separate thread
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=Plan,
                ),
            )
            
            # The response.text will be a JSON string conforming to the Plan schema
            return Plan.model_validate_json(response.text)
        
        except Exception as e:
            print(f"Erro ao gerar o plano: {e}")
            # Fallback to a simple plan if structured output fails
            return Plan(task_goal=task_description, phases=[
                Step(step_id=1, description="Erro no planejamento. Tentar novamente.", tool_required="none")
            ])

    async def execute_step(self, step: Step, context: str) -> str:
        """
        Simulates the execution of a single step. This will be expanded in Phase 5.
        This function dispatches the task to the appropriate tool.
        """
        print(f"-> Executando Passo {step.step_id}: {step.description} (Ferramenta: {step.tool_required})")
        
        # Dispatch to the appropriate tool based on the plan
        if step.tool_required == 'code_generator':
            # For code generation, the description is the prompt for the code
            return await asyncio.to_thread(code_generator, self.client, prompt=step.description)
        
        elif step.tool_required == 'code_execution':
            # Execute the code generated in the previous step (which is in the context)
            # We assume the previous step's result is the code to execute
            # For a more robust system, we would need to parse the code from the context
            return await asyncio.to_thread(execute_python_code, context)
        
        elif step.tool_required == 'content_generator':
            # For content generation, the description is the prompt for the content
            return await asyncio.to_thread(content_generator, self.client, prompt=step.description)
            
        elif step.tool_required == 'web_scraper':
            # The web scraper now takes the objective and uses its internal logic
            return await asyncio.to_thread(web_scraper, self.client, objective=step.description)
            
        elif step.tool_required == 'data_analyzer':
            # In a real scenario, we would pass the actual data from the context
            # For this prototype, we'll use a simplified simulation
            return await asyncio.to_thread(data_analyzer, self.client, data_summary=context, analysis_objective=step.description)
            
        elif step.tool_required == 'none':
            # If no tool is required, use the model to confirm or perform a simple task
            prompt = (
                f"Confirme a conclusão do passo: '{step.description}'. "
                f"Contexto anterior: {context}. "
                f"Forneça uma breve confirmação e um resumo do estado atual."
            )
            try:
                # Run the synchronous call in a separate thread
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                return f"Erro na execução do passo 'none': {e}"
        
        else:
            return f"Ferramenta desconhecida: {step.tool_required}"

    async def run(self, task_description: str, update_db_status: callable):
        """
        Main execution loop: plans the task and executes the steps sequentially.
        """
        # 1. Update DB status to IN_PROGRESS
        update_db_status(self.task_id, "IN_PROGRESS")
        
        plan = await self.create_plan(task_description)
        print("\n--- Plano Gerado ---")
        print(f"Objetivo: {plan.task_goal}")
        for step in plan.phases:
            print(f"  [{step.step_id}] {step.description} (Ferramenta: {step.tool_required})")
        print("--------------------\n")

        current_context = "Início da execução. Nenhum resultado anterior."
        
        for step in plan.phases:
            # 2. Execute step
            result = await self.execute_step(step, current_context)
            print(f"\n[Resultado do Passo {step.step_id}]")
            print(result)
            
            # Update context for the next step
            current_context = f"Resultado do Passo {step.step_id}: {result}"
            
            # 3. Update DB with current context (optional, for detailed logging)
            # update_db_status(self.task_id, "IN_PROGRESS", current_context)

        print("\n--- Tarefa Concluída ---")
        
        # 4. Final update to DB status
        update_db_status(self.task_id, "COMPLETED", current_context)
        
        return current_context


