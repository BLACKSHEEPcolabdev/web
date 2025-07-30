# servidor.py
import os
from flask import Flask, request, jsonify

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Pega a chave secreta de uma variável de ambiente. Se não encontrar, usa um valor padrão.
# No Render, vamos definir essa variável para o valor real.
CHAVE_API_SECRETA = os.environ.get('SECRET_API_KEY', 'default_key_se_nao_encontrar')

# --- SUA LÓGICA SECRETA VAI AQUI ---
def funcao_magica_secreta(dado):
    """
    Esta é a função que ninguém pode ver.
    Ela faz cálculos, processa dados, etc.
    """
    resultado = f"O dado '{dado}' foi processado com sucesso pelo algoritmo secreto v3.0!"
    return resultado
# ------------------------------------

# Este é o "endpoint" ou a URL que seu cliente vai chamar
@app.route('/processar', methods=['POST'])
def processar_dados():
    # 1. Verifica se o cliente enviou a chave de API correta no cabeçalho
    chave_cliente = request.headers.get('X-Api-Key')
    if chave_cliente != CHAVE_API_SECRETA:
        # Se a chave estiver errada ou faltando, nega o acesso
        return jsonify({"erro": "Chave de API inválida ou ausente"}), 401 # 401 = Não Autorizado

    # 2. Pega os dados que o cliente enviou no corpo da requisição
    dados_recebidos = request.json.get('dados_para_processar')
    if not dados_recebidos:
        return jsonify({"erro": "Nenhum 'dados_para_processar' encontrado na requisição"}), 400 # 400 = Requisição Ruim

    # 3. Se tudo estiver certo, chama sua função secreta
    resultado_final = funcao_magica_secreta(dados_recebidos)

    # 4. Envia o resultado de volta para o cliente
    return jsonify({"resultado": resultado_final})

# Rota de teste para ver se o servidor está online
@app.route('/')
def index():
    return "API Secreto está online!"