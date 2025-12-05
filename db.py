import sqlite3
import os
from typing import List, Dict, Any

DATABASE_FILE = "tasks.db"

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
    return conn

def init_db():
    """Inicializa o banco de dados e cria a tabela de tarefas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela para armazenar o estado das tarefas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            task_description TEXT NOT NULL,
            callback_url TEXT,
            status TEXT NOT NULL,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado em {DATABASE_FILE}")

def create_task(task_id: str, task_description: str, callback_url: str = None) -> None:
    """Cria uma nova tarefa no banco de dados com status 'PENDING'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (id, task_description, callback_url, status) VALUES (?, ?, ?, ?)",
        (task_id, task_description, callback_url, "PENDING")
    )
    conn.commit()
    conn.close()

def update_task_status(task_id: str, status: str, result: str = None) -> None:
    """Atualiza o status e o resultado de uma tarefa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if result:
        cursor.execute(
            "UPDATE tasks SET status = ?, result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, result, task_id)
        )
    else:
        cursor.execute(
            "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, task_id)
        )
        
    conn.commit()
    conn.close()

def get_task(task_id: str) -> Dict[str, Any] | None:
    """Busca uma tarefa pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

if __name__ == "__main__":
    # Exemplo de uso e teste
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        
    init_db()
    
    test_id = "test-123"
    create_task(test_id, "Tarefa de teste", "http://callback.test")
    print(f"Tarefa criada: {get_task(test_id)}")
    
    update_task_status(test_id, "IN_PROGRESS")
    print(f"Status atualizado: {get_task(test_id)}")
    
    update_task_status(test_id, "COMPLETED", "Resultado final da tarefa.")
    print(f"Tarefa concluída: {get_task(test_id)}")
