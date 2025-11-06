from typing import Any
import psycopg2
from psycopg2.extras import DictCursor
from urllib.parse import quote_plus

class DatabaseManager:
    "Classe de Gerenciamento do database"

    def __init__(self) -> None:

        host = "localhost"
        database = "tutorial"
        user = "postgres"
        password = "051024" 
        port = "5432"

        dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.conn = psycopg2.connect(dsn)

        self.cursor = self.conn.cursor(cursor_factory=DictCursor)

    def execute_statement(self, statement: str) -> bool:
        "Usado para Inserções, Deleções, Alter Tables"
        try:
            self.cursor.execute(statement)
            self.conn.commit()
        except:
            self.conn.reset()
            return False
        return True

    def execute_select_all(self, query: str) -> list[dict[str, Any]]:
        "Usado para SELECTS no geral"
        self.cursor.execute(query)
        return [dict(item) for item in self.cursor.fetchall()]

    def execute_select_one(self, query: str) -> dict | None:
        "Usado para SELECT com apenas uma linha de resposta"
        self.cursor.execute(query)
        query_result = self.cursor.fetchone()

        if not query_result:
            return None

        return dict(query_result)