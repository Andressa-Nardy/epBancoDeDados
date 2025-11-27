from flask import Blueprint, request, jsonify
from servicos.usuario_servico import criar_novo_usuario

# Define um "Blueprint" (um conjunto de rotas) para usuários
usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/cadastrar', methods=['POST'])
def post_novo_usuario():
    """
    Rota para cadastrar um novo usuário.
    Espera um JSON no corpo da requisição.
    """
    dados = request.json # Pega os dados JSON enviados pelo frontend

    resultado, status_code = criar_novo_usuario(dados)

    return jsonify(resultado), status_code