from servicos.database.conector import DatabaseManager


class GraficaDatabase:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    def get_grafica(self):
        query = f"SELECT * FROM grafica;"
        return self.db.execute_select_all(query)