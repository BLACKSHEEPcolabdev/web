# servidor_auth.py
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Uma lista de chaves de licença válidas.
# No Render, vamos colocar isso como uma variável de ambiente,
# separando as chaves por vírgula. Ex: "chave_do_joao,chave_da_maria,gh000st"
VALID_API_KEYS = os.environ.get('VALID_CLIENT_KEYS', '').split(',')

@app.route('/check-auth', methods=['POST'])
def check_authorization():
    # Pega a chave que o cliente enviou no cabeçalho
    client_key = request.headers.get('X-License-Key')

    if client_key and client_key in VALID_API_KEYS:
        # Se a chave for válida, retorna sucesso
        return jsonify({
            "status": "success",
            "message": "Autorização concedida. Bem-vindo!"
        }), 200
    else:
        # Se a chave for inválida ou não existir, nega o acesso
        return jsonify({
            "status": "error",
            "message": "Chave de licença inválida ou expirada. Acesso negado."
        }), 401 # 401 = Não Autorizado

@app.route('/')
def index():
    return "Servidor de Autenticação HithoundM3u está online."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
