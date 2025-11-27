from flask import Blueprint, jsonify, request
from servicos.analise_servico import (
    usuarios_top_emprestimos, infra_mais_reservada, itens_nunca_emprestados,
    taxa_pontualidade_usuarios, ranking_itens_mais_emprestados,
    infra_sem_uso, itens_por_titulo_autor, infra_capacidade_acima_tipo
)
from servicos.database.conector import DatabaseManager 

analise_bp = Blueprint("analise", __name__, url_prefix="/analise")

# Instancia o banco de dados
db = DatabaseManager()

# --- ROTAS ESTÁTICAS (Painel de Análise) ---

@analise_bp.route("/usuarios-top-emprestimos", methods=["GET"])
def get_usuarios_top_emprestimos():
    resultado = usuarios_top_emprestimos()
    return jsonify(resultado), 200

@analise_bp.route("/infra-mais-reservada", methods=["GET"])
def get_infra_mais_reservada():
    resultado = infra_mais_reservada()
    return jsonify(resultado), 200

@analise_bp.route("/itens-nunca-emprestados", methods=["GET"])
def get_itens_nunca_emprestados():
    resultado = itens_nunca_emprestados()
    return jsonify(resultado), 200

@analise_bp.route("/itens-por-titulo-autor", methods=["GET"])
def get_itens_por_titulo_autor():
    titulo = request.args.get("titulo", "")
    autor = request.args.get("autor", "")
    if not titulo and not autor:
        return jsonify({"erro": "Informe titulo ou autor"}), 400
    try:
        resultado = itens_por_titulo_autor(titulo, autor)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@analise_bp.route("/infra-acima-tipo", methods=["GET"])
def get_infra_acima_tipo():
    tipo = request.args.get("tipo")
    if not tipo:
        return jsonify({"erro": "Informe o tipo"}), 400
    resultado = infra_capacidade_acima_tipo(tipo)
    return jsonify(resultado), 200

@analise_bp.route("/taxa-pontualidade", methods=["GET"])
def get_taxa_pontualidade():
    resultado = taxa_pontualidade_usuarios()
    return jsonify(resultado), 200

@analise_bp.route("/ranking-itens-emprestados", methods=["GET"])
def get_ranking_itens_emprestados():
    resultado = ranking_itens_mais_emprestados()
    return jsonify(resultado), 200

@analise_bp.route("/infra-sem-uso", methods=["GET"])
def get_infra_sem_uso():
    resultado = infra_sem_uso()
    return jsonify(resultado), 200


# --- ROTA DINÂMICA (Gerenciamento Inteligente) ---

@analise_bp.route("/gerenciamento/consulta", methods=["POST"])
def consulta_dinamica():
    try:
        data = request.get_json()
        
        # --- SUBQUERIES (TABELAS VIRTUAIS) ---

        # 1. ACERVO (Ranking + Contagem)
        sql_acervo = """(
            SELECT 
                A.Titulo as titulo, 
                A.Autor as autor, 
                A.Genero as genero,
                A.Ano_Publicacao as ano_publicacao,
                COUNT(EM.ID_Item) as total_emprestimos,
                RANK() OVER (ORDER BY COUNT(EM.ID_Item) DESC) as posicao_ranking
            FROM ITEM_ACERVO A
            LEFT JOIN EMPRESTIMO EM ON A.ID_Item = EM.ID_Item
            GROUP BY A.Titulo, A.Autor, A.Genero, A.Ano_Publicacao
        ) AS tv_acervo"""

        # 2. USUÁRIOS (Ranking + Contagem + Pontualidade) - ATUALIZADO
        sql_usuarios = """(
            SELECT 
                U.Nome as nome, 
                U.CPF as cpf, 
                U.Email as email, 
                U.Data_Cadastro as data_cadastro,
                COUNT(E.CPF_Usuario) as total_emprestimos,
                -- NOVA LINHA: Ranking baseado no total de empréstimos
                RANK() OVER (ORDER BY COUNT(E.CPF_Usuario) DESC) as ranking_emprestimos,
                
                ROUND(
                    100.0 * SUM(
                        CASE WHEN E.Data_Devolucao_Real <= E.Data_Devolucao_Prevista 
                        THEN 1 ELSE 0 END
                    ) / NULLIF(COUNT(E.CPF_Usuario), 0), 
                2) as taxa_pontualidade
            FROM USUARIO U
            LEFT JOIN EMPRESTIMO E ON U.CPF = E.CPF_Usuario
            GROUP BY U.Nome, U.CPF, U.Email, U.Data_Cadastro
        ) AS tv_usuarios"""

        # 3. INFRAESTRUTURA (Ranking + Contagens)
        sql_infra = """(
            SELECT 
                I.Local as local, 
                I.Tipo as tipo, 
                I.Capacidade as capacidade,
                (SELECT COUNT(*) FROM RESERVA_INFRA R WHERE R.ID_Infra = I.ID_Infra) as total_reservas,
                (SELECT COUNT(*) FROM EVENTOS EV WHERE EV.ID_Infra = I.ID_Infra) as total_eventos,
                RANK() OVER (
                    ORDER BY (SELECT COUNT(*) FROM RESERVA_INFRA R WHERE R.ID_Infra = I.ID_Infra) DESC
                ) as ranking_reservas
            FROM INFRAESTRUTURA I
        ) AS tv_infra"""

        # Mapeamento
        mapa_tabelas = {
            "acervo": sql_acervo,
            "usuarios": sql_usuarios,
            "infraestrutura": sql_infra,
            "emprestimos": "EMPRESTIMO",
            "eventos": "EVENTOS"
        }
        
        tabela_frontend = data.get('tabela')
        filtros = data.get('filtros', [])
        colunas = data.get('colunas', [])
        
        if tabela_frontend not in mapa_tabelas:
            return jsonify({"erro": "Tabela inválida"}), 400
            
        nome_tabela_real = mapa_tabelas[tabela_frontend]
        
        # Query Builder
        campos_sql = ", ".join(colunas) if colunas else "*"
        query = f"SELECT {campos_sql} FROM {nome_tabela_real}"
        
        params = []
        clasulas_where = []
        
        for f in filtros:
            campo = f['campo']
            operador = f['operador']
            valor = f['valor']
            
            if operador == 'eq':
                clasulas_where.append(f"{campo} = %s")
                params.append(valor)
            elif operador == 'neq':
                clasulas_where.append(f"{campo} != %s")
                params.append(valor)
            elif operador == 'contains':
                clasulas_where.append(f"{campo} ILIKE %s")
                params.append(f"%{valor}%")
            elif operador == 'gt':
                clasulas_where.append(f"{campo} > %s")
                params.append(valor)
            elif operador == 'lt':
                clasulas_where.append(f"{campo} < %s")
                params.append(valor)
            elif operador == 'gte':
                clasulas_where.append(f"{campo} >= %s")
                params.append(valor)
            elif operador == 'lte':
                clasulas_where.append(f"{campo} <= %s")
                params.append(valor)

        if clasulas_where:
            query += " WHERE " + " AND ".join(clasulas_where)
            
        resultado = db.execute_select_all(query, tuple(params))
        return jsonify(resultado), 200

    except Exception as e:
        print(f"Erro na consulta dinâmica: {e}")
        return jsonify({"erro": str(e)}), 500