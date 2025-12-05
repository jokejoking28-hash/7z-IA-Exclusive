import os
import subprocess
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from typing import List, Dict

MODEL_NAME = 'gemini-2.5-flash'

# --- Tool 1: Code Generation (Uses Gemini) ---

def code_generator(client: genai.Client, prompt: str, language: str = "python") -> str:
    """
    Generates code based on a detailed prompt.
    """
    print(f"--- Gerando Código ({language}) ---")
    
    system_instruction = (
        f"Você é um gerador de código especializado. Sua única tarefa é escrever o código completo e funcional na linguagem {language} "
        f"que atenda à descrição fornecida. O código DEVE ser o único conteúdo da sua resposta, formatado em um bloco de código Markdown."
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
            lines = text.split('\n')
            if len(lines) > 2:
                return '\n'.join(lines[1:-1])
        
        return text
        
    except Exception as e:
        return f"Erro na geração de código: {e}"

# --- Tool 2: Secure Code Execution (Real Tool) ---

def execute_python_code(code: str) -> str:
    """
    Executes Python code in a secure subprocess and captures output.
    """
    print("--- Executando Código Python ---")
    temp_file = "temp_script.py"
    
    try:
        # 1. Save code to a temporary file
        with open(temp_file, "w") as f:
            f.write(code)
            
        # 2. Execute the file using a subprocess
        # Using a timeout to prevent infinite loops
        result = subprocess.run(
            ["python3", temp_file],
            capture_output=True,
            text=True,
            timeout=10  # 10 seconds timeout
        )
        
        output = f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR (Erro):\n{result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "Erro de Execução: O código excedeu o tempo limite de 10 segundos."
    except Exception as e:
        return f"Erro de Execução: {e}"
    finally:
        # 3. Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

# --- Tool 3: Web Scraper (Real Tool - AI News Gatherer) ---

def web_scraper(client: genai.Client, objective: str) -> str:
    """
    Scrapes a set of predefined AI news sites and summarizes the content.
    """
    print("--- Web Scraper (Coletor de Notícias de IA) ---")
    
    # Predefined list of sites for a robust prototype
    ai_news_sites = [
        {"url": "https://www.canaltech.com.br/inteligencia-artificial/", "selector": "h2.title"},
        {"url": "https://www.tecmundo.com.br/inteligencia-artificial", "selector": "h3.tec--card__title"},
    ]
    
    all_titles = []
    
    for site in ai_news_sites:
        try:
            response = requests.get(site["url"], timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract titles based on the selector
            titles = [tag.get_text(strip=True) for tag in soup.select(site["selector"])][:3]
            all_titles.extend(titles)
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {site['url']}: {e}")
            
    if not all_titles:
        return "Erro: Não foi possível coletar notícias de IA. As fontes podem estar inacessíveis ou os seletores desatualizados."

    # Use Gemini to summarize the collected titles based on the objective
    summary_prompt = (
        f"Com base nos seguintes títulos de notícias de IA, gere um resumo conciso e relevante para o objetivo: '{objective}'. "
        f"Títulos coletados: {'; '.join(all_titles)}"
    )
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=summary_prompt
        )
        return response.text
    except Exception as e:
        return f"Erro na sumarização de notícias: {e}"

# --- Tool 4: Content Generation (Uses Gemini) ---

def content_generator(client: genai.Client, prompt: str) -> str:
    """
    Generates detailed textual content (reports, summaries, articles) based on a prompt.
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

# --- Tool 5: Data Analyzer (Simulation - Future Expansion) ---

def data_analyzer(client: genai.Client, data_summary: str, analysis_objective: str) -> str:
    """
    Simulates a data analysis operation.
    """
    print("--- Data Analyzer (Simulação) ---")
    
    prompt = (
        f"Simule uma análise de dados com o objetivo: '{analysis_objective}'. "
        f"Os dados de entrada são: '{data_summary}'. "
        f"Forneça uma conclusão analítica e um insight."
    )
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Erro na simulação de análise de dados: {e}"
