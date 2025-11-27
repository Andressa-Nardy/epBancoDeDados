from servicos.database.conector import DatabaseManager

db = DatabaseManager()

def usuarios_top_emprestimos():
    query = """
        SELECT U.Nome, COUNT(*) AS total_emprestimos
        FROM EMPRESTIMO E
        JOIN USUARIO U ON U.CPF = E.CPF_Usuario
        GROUP BY U.CPF, U.Nome
        HAVING COUNT(*) >= ALL (
            SELECT COUNT(*)
            FROM EMPRESTIMO
            GROUP BY CPF_Usuario
        );
    """
    return db.execute_select_all(query)


def infra_mais_reservada():
    query = """
        SELECT I.Local, COUNT(*) AS qtd_reservas
        FROM RESERVA_INFRA R
        JOIN INFRAESTRUTURA I ON I.ID_Infra = R.ID_Infra
        GROUP BY I.ID_Infra, I.Local
        HAVING COUNT(*) >= ALL (
            SELECT COUNT(*)
            FROM RESERVA_INFRA
            GROUP BY ID_Infra
        )
        ORDER BY qtd_reservas DESC;
    """
    return db.execute_select_all(query)


def itens_nunca_emprestados():
    query = """
        SELECT A.Titulo
        FROM ITEM_ACERVO A
        LEFT JOIN EXEMPLAR E ON A.ID_Item = E.ID_Item
        LEFT JOIN EMPRESTIMO EM 
                ON EM.ID_Item = E.ID_Item
               AND EM.Num = E.Num
        WHERE E.ID_Item IS NULL   -- sem exemplar
           OR EM.ID_Item IS NULL; -- exemplar sem empréstimo
    """
    return db.execute_select_all(query)


def itens_por_titulo_autor(titulo, autor):
    query = """
        SELECT Titulo, Autor
        FROM ITEM_ACERVO
        WHERE Titulo ILIKE %s
          AND Autor ILIKE %s;
    """

    # Monta os padrões de busca com wildcard
    params = (f"%{titulo}%", f"%{autor}%")

    return db.execute_select_all(query, params)


def infra_capacidade_acima_tipo(tipo_base: str):
    query = """
        SELECT local, capacidade
        FROM infraestrutura
        WHERE capacidade > ALL (
            SELECT capacidade
            FROM infraestrutura
            WHERE tipo = %s
        )
        AND tipo <> %s;
    """

    params = (tipo_base, tipo_base)
    return db.execute_select_all(query, params)



def taxa_pontualidade_usuarios():
    query = """
        SELECT 
            U.Nome,
            ROUND(
                100.0 * SUM(
                    CASE WHEN E.Data_Devolucao_Real <= E.Data_Devolucao_Prevista 
                         THEN 1 ELSE 0 END
                ) / COUNT(*),
                2
            ) AS taxa_pontualidade
        FROM EMPRESTIMO E
        JOIN USUARIO U ON E.CPF_Usuario = U.CPF
        GROUP BY U.Nome
        ORDER BY taxa_pontualidade DESC;
    """
    return db.execute_select_all(query)


def ranking_itens_mais_emprestados():
    query = """
        SELECT 
            A.Titulo,
            A.Autor,
            COUNT(EM.CPF_Usuario) AS total_emprestimos,
            RANK() OVER (ORDER BY COUNT(EM.CPF_Usuario) DESC) AS posicao
        FROM ITEM_ACERVO A
        JOIN EMPRESTIMO EM ON A.ID_Item = EM.ID_Item
        GROUP BY A.ID_Item, A.Titulo, A.Autor
        ORDER BY posicao;
    """
    return db.execute_select_all(query)


def infra_sem_uso():
    query = """
        SELECT I.Local, I.Tipo
        FROM INFRAESTRUTURA I
        LEFT JOIN RESERVA_INFRA R ON R.ID_Infra = I.ID_Infra
        LEFT JOIN EVENTOS EV ON EV.ID_Infra = I.ID_Infra
        WHERE R.ID_Infra IS NULL
          AND EV.ID_Infra IS NULL;
    """
    return db.execute_select_all(query)
