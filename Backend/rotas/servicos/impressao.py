from datetime import datetime
from servicos.database.conector import DatabaseManager


class ImpressaoDatabase:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    def get_impressos(self):
        data = datetime.now().date().isoformat()  # Data atual
        query = f"SELECT * FROM imprime WHERE data_entrega < '{data}';"
        return self.db.execute_select_all(query)

    def regristra_impressao(
        self, lisbn: str, grafica_id: str, nto_copias: str, data_entrega: str
    ) -> bool:
        statement = f"INSERT INTO imprime (lisbn, grafica_id, nto_copias, data_entrega) VALUES ('{lisbn}', {grafica_id}, {nto_copias}, '{data_entrega}');"
        return self.db.execute_statement(statement)