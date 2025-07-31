# servidor_auth.py (VERSÃO MELHORADA)
import os
import hmac
import logging
from flask import Flask, request, jsonify

# Configura o logging para ser mais informativo
# No Render, isso será automaticamente capturado nos logs do serviço
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)

# Carrega as chaves de licença de uma variável de ambiente.
# A lista de chaves é processada para remover espaços em branco, tornando a configuração mais robusta.
VALID_API_KEYS = [key.strip() for key in os.environ.get('VALID_CLIENT_KEYS', '').split(',')]

@app.route('/check-auth', methods=['POST'])
def check_authorization():
    # Pega a chave que o cliente enviou no cabeçalho e o IP de origem
    client_key = request.headers.get('X-License-Key')
    client_ip = request.remote_addr

    is_key_valid = False
    if client_key:
        for valid_key in VALID_API_KEYS:
            # Usa hmac.compare_digest para uma comparação de strings segura em tempo constante,
            # prevenindo ataques de temporização (timing attacks).
            if hmac.compare_digest(client_key, valid_key):
                is_key_valid = True
                break # A chave foi encontrada e validada, podemos sair do loop

    if is_key_valid:
        # Loga o sucesso da autenticação para monitoramento
        # Mostra apenas os primeiros 4 caracteres da chave por segurança
        app.logger.info(f"Sucesso de autenticação para a chave '{client_key[:4]}...' do IP: {client_ip}")
        return jsonify({
            "status": "success",
            "message": "Autorização concedida. Bem-vindo!"
        }), 200
    else:
        # Loga a tentativa de acesso falha para auditoria de segurança
        app.logger.warning(f"FALHA de autenticação para a chave '{client_key}' do IP: {client_ip}")
        return jsonify({
            "status": "error",
            "message": "Chave de licença inválida ou expirada. Acesso negado."
        }), 401

@app.route('/')
def index():
    # Uma rota simples para verificar se o servidor está online ("health check")
    return "Servidor de Autenticação HithoundM3u está online e operacional."

if __name__ == "__main__":
    # A porta é definida pela variável de ambiente PORT, padrão do Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
