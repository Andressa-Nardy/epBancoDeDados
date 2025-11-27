from typing import Any
import psycopg2
from psycopg2.extras import DictCursor

class DatabaseManager:
    """Classe de Gerenciamento do database"""

    def __init__(self) -> None:
        try:
            self.conn = psycopg2.connect(
                dbname="tutorial",
                user="postgres",
                password="051024",  # Confirme se a senha está correta
                host="127.0.0.1",
                port=5432,
            )
            self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("Erro ao conectar ao banco:", e)

    def execute_statement(self, statement: str, params=None) -> bool:
        """Usado para Inserções, Deleções, Alter Tables"""
        try:
            if params:
                self.cursor.execute(statement, params)
            else:
                self.cursor.execute(statement)

            self.conn.commit()
            return True
        except Exception as e:
            print("Erro no execute_statement:", e)
            self.conn.rollback()  # <--- IMPORTANTE: Limpa o erro
            return False

    def execute_select_all(self, query: str, params=None) -> list[dict[str, Any]]:
        """Usado para SELECTS no geral"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            return [dict(item) for item in self.cursor.fetchall()]
        except Exception as e:
            print(f"Erro no Select All: {e}")
            self.conn.rollback()  # <--- IMPORTANTE: Destrava o banco para a próxima tentativa
            raise e # Lança o erro para o Flask mostrar na tela qual foi o problema real

    def execute_select_one(self, query: str, params=None) -> dict | None:
        """Usado para SELECT com apenas uma linha de resposta"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            query_result = self.cursor.fetchone()

            if not query_result:
                return None

            return dict(query_result)
        except Exception as e:
            print(f"Erro no Select One: {e}")
            self.conn.rollback() # <--- IMPORTANTE
            return None