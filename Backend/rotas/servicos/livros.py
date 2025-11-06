from servicos.database.conector import DatabaseManager


class LivrosDatabase:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    def get_livros(self, rg: str, editora: str, livro: str):
        query = """
                SELECT * FROM livros l
                LEFT JOIN editora e ON e.id = l.editora_id 
                LEFT JOIN escreve es ON es.isbn = l.isbn
                LEFT JOIN autor a ON a.rg = es.rg
                """

        if rg:
            query += f"WHERE a.rg = '{rg}'\n"

        if editora:
            if "WHERE" in query:
                query += f"AND e.id = {editora}\n"
            else:
                query += f"WHERE e.id = {editora}\n"

        if livro:
            if "WHERE" in query:
                query += f"AND l.isbn = '{livro}'\n"
            else:
                query += f"WHERE es.isbn = '{livro}'\n"

        return self.db.execute_select_all(query)