import os
from google import genai
from google.genai import types

MODEL_NAME = 'gemini-2.5-flash'

def code_generator(client: genai.Client, prompt: str, language: str = "python") -> str:
    """
    Generates code based on a detailed prompt.
    
    Args:
        prompt: A detailed description of the code to be generated.
        language: The programming language for the code (default: python).
        
    Returns:
        The generated code as a string.
    """
    print(f"--- Gerando Código ({language}) ---")
    
    system_instruction = (
        f"Você é um gerador de código especializado. Sua única tarefa é escrever o código completo e funcional na linguagem {language} "
        f"que atenda à descrição fornecida. NÃO inclua explicações, comentários excessivos ou texto introdutório/final. "
        f"O código DEVE ser o único conteúdo da sua resposta, formatado em um bloco de código Markdown."
    )
    
    full_prompt = f"Gere o seguinte código em {language}: {prompt}"
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        # Extract the code block from the response text
        text = response.text.strip()
        if text.startswith("```") and text.endswith("```"):
            # Remove the markdown code block delimiters and language tag
            lines = text.split('\n')
            if len(lines) > 2:
                return '\n'.join(lines[1:-1])
        
        return text # Return raw text if not a clean code block
        
    except Exception as e:
        return f"Erro na geração de código: {e}"

def content_generator(client: genai.Client, prompt: str) -> str:
    """
    Generates detailed textual content (reports, summaries, articles) based on a prompt.
    
    Args:
        prompt: A detailed description of the content to be generated.
        
    Returns:
        The generated content as a string.
    """
    print("--- Gerando Conteúdo Textual ---")
    
    system_instruction = (
        "Você é um redator de conteúdo profissional. Sua tarefa é gerar um texto coeso, bem estruturado e detalhado "
        "que atenda ao prompt fornecido. O texto deve ser formatado em Markdown."
    )
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return response.text
    except Exception as e:
        return f"Erro na geração de conteúdo: {e}"

# Placeholder for other tools (web_scraper, data_analyzer)
def web_scraper(client: genai.Client, url: str, objective: str) -> str:
    """Simulates a web scraping operation."""
    return f"Simulação de Web Scraper: Coletando dados de {url} com o objetivo: {objective}"

def data_analyzer(client: genai.Client, data_summary: str, analysis_objective: str) -> str:
    """Simulates a data analysis operation."""
    return f"Simulação de Data Analyzer: Analisando dados ({data_summary}) com o objetivo: {analysis_objective}"
