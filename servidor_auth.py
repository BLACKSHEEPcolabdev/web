# ============================================================================
#               SERVIDOR DE AUTENTICAÇÃO HITHOUNDM3U - v2.0
#                (com Página HTML, Segurança e Logging)
#
#                    desenvolvido por @gh000000000000st
# ============================================================================
import os
import hmac
import logging
from flask import Flask, request, jsonify

# --- Configuração do Logging ---
# Configura o logging para ser mais informativo. No Render, isso será
# automaticamente capturado nos logs do serviço para fácil monitoramento.
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

# --- Inicialização do Flask ---
app = Flask(__name__)

# --- Carregamento das Chaves de Licença ---
# Carrega as chaves de uma variável de ambiente, que é a prática recomendada
# para segurança em serviços de nuvem como o Render.
# A lista de chaves é processada com .strip() para remover espaços em branco,
# tornando a configuração no painel do Render mais robusta a erros de digitação.
VALID_API_KEYS = [key.strip() for key in os.environ.get('VALID_CLIENT_KEYS', 'DEFAULT_KEY_PARA_TESTE_LOCAL').split(',')]
if 'DEFAULT_KEY_PARA_TESTE_LOCAL' in VALID_API_KEYS:
    app.logger.warning("AVISO: Usando chave de licença padrão. Configure a variável de ambiente 'VALID_CLIENT_KEYS' no Render.")

# --- Rota Principal (Health Check Visual) ---
@app.route('/')
def index():
    """
    Exibe uma página HTML estilizada para confirmar que o servidor está online.
    Serve como um "health check" visual para qualquer pessoa que acesse a URL base.
    """
    # URL da imagem que você quer exibir. Recomendo usar uma imagem hospedada no GitHub.
    IMAGE_URL = "https://raw.githubusercontent.com/BLACKSHEEPcolabdev/add-on/refs/heads/master/BLACKGHOST/Imagens/topo2.png"
    
    # Template HTML completo com CSS embutido
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Auth Server - Online</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@700&family=Poppins:wght@700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-dark: #000000;
                --surface-dark: #0d0d0d;
                --primary-accent: #00ff00;
                --text-light: #00ff00;
                --text-muted: #008f00;
                --border-color: #003300;
            }}
            html {{ height: 100%; }}
            body {{
                margin: 0; padding: 2em; font-family: 'Fira Code', monospace;
                background-color: var(--bg-dark); color: var(--text-light);
                display: flex; justify-content: center; align-items: center;
                min-height: 100%;
                background-image: radial-gradient(circle at 1px 1px, rgba(0, 255, 0, 0.1) 1px, transparent 0);
                background-size: 25px 25px;
                text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
            }}
            .container {{
                background-color: var(--surface-dark);
                padding: 3em; border: 1px solid var(--border-color);
                max-width: 600px; text-align: center;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            }}
            img {{ max-width: 300px; margin-bottom: 2em; }}
            h1 {{
                font-family: 'Poppins', sans-serif; font-size: 1.8em;
                color: var(--primary-accent); margin-bottom: 0.5em;
            }}
            p {{ font-size: 1.1em; color: var(--text-muted); line-height: 1.6; }}
            .status {{
                display: inline-flex; align-items: center; gap: 0.5em;
                margin-top: 1.5em; padding: 0.5em 1em;
                background-color: rgba(0, 255, 0, 0.1);
                border: 1px solid var(--border-color);
            }}
            .status-indicator {{
                width: 10px; height: 10px;
                background-color: var(--primary-accent); border-radius: 50%;
                box-shadow: 0 0 8px var(--primary-accent);
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }}
                70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }}
                100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="{IMAGE_URL}" alt="HithoundM3u Logo">
            <h1>Servidor de Autenticação</h1>
            <p>Este serviço é responsável por validar as chaves de licença dos scripts HithoundM3u.</p>
            <div class="status">
                <div class="status-indicator"></div>
                <span>STATUS: OPERACIONAL</span>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# --- Rota de Autenticação (/check-auth) ---
@app.route('/check-auth', methods=['POST'])
def check_authorization():
    """
    Valida a chave de licença enviada pelo script cliente.
    Esta é a rota principal da API.
    """
    # Pega a chave que o cliente enviou no cabeçalho e o IP de origem
    client_key = request.headers.get('X-License-Key')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) # Melhor para proxies como o do Render

    is_key_valid = False
    if client_key:
        for valid_key in VALID_API_KEYS:
            # Usa hmac.compare_digest para uma comparação segura que previne "timing attacks".
            if hmac.compare_digest(client_key, valid_key):
                is_key_valid = True
                break

    if is_key_valid:
        # Loga o sucesso da autenticação para monitoramento
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

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    # O Render define a variável de ambiente PORT. Usamos ela para maior compatibilidade.
    port = int(os.environ.get("PORT", 5000))
    # 'debug=False' é crucial para ambientes de produção como o Render.
    app.run(host='0.0.0.0', port=port, debug=False)
