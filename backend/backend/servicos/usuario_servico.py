from .database.conector import db 
import psycopg2

def criar_novo_usuario(dados_usuario):
    """
    Insere um novo usuário no banco de dados.
    'dados_usuario' deve ser um dicionário com chaves: 'cpf', 'nome', 'email' e 'data_cadastro'.
    """

    # Validando se temos todos os dados
    if not all(k in dados_usuario for k in ['cpf', 'nome', 'email', 'data_cadastro']):
        return {"erro": "Dados incompletos. 'cpf', 'nome', 'email' e 'data_cadastro' são obrigatórios."}, 400

    query = """
        INSERT INTO USUARIO (CPF, Nome, Email, Data_Cadastro) 
        VALUES (%s, %s, %s, %s)
        RETURNING CPF; 
    """
    # Usamos %s para segurança (evita SQL Injection)
    params = (
        dados_usuario['cpf'],
        dados_usuario['nome'],
        dados_usuario['email'],
        dados_usuario['data_cadastro']
    )

    try:
        resultado = db.execute_insert(query, params)
        return {"mensagem": f"Usuário com CPF {resultado['cpf']} criado com sucesso!"}, 201

    except psycopg2.Error as e:
        # Captura erros do banco (ex: CPF duplicado)
        return {"erro": f"Erro no banco de dados: {e.pgerror}"}, 500
    except Exception as e:
        return {"erro": f"Erro inesperado: {str(e)}"}, 500