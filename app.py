import os
import logging
import threading
import uuid
import time
import datetime
from flask import Flask, request, jsonify, render_template_string
from orcid.orcid_client import OrcidClient
from orcid.email_sender import EmailSender 
from orcid.authorization import OrcidAuthorization

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIENT_ID = os.environ.get('ORCID_CLIENT_ID')
CLIENT_SECRET = os.environ.get('ORCID_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI')

SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = os.environ.get('SMTP_PORT')
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
SENDER_EMAIL = "scielo_desenv@mailinator.com"

app = Flask(__name__)

pending_requests = {}
pending_authorizations = {}

orcid_client = OrcidClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

email_sender = EmailSender(
    SMTP_SERVER, SMTP_PORT, 
    EMAIL_USERNAME, EMAIL_PASSWORD, 
    SENDER_EMAIL
)

@app.route('/push_to_orcid', methods=['POST'])
def push_to_orcid():
    try:
        data = request.json
        
        required_fields = ['author_email', 'author_name', 'work_data']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Campo obrigatório ausente: {field}"}), 400
        
        request_id = str(uuid.uuid4())
        
        pending_requests[request_id] = {
            'author_email': data['author_email'],
            'author_name': data['author_name'],
            'work_data': data['work_data'],
            'timestamp': time.time(),
            'status': 'processing'
        }
        
        thread = threading.Thread(target=process_authorization, args=(request_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "request_id": request_id,
            "message": "Solicitação de publicação iniciada. E-mail de autorização será enviado."
        }), 202
        
    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/request_status/<request_id>', methods=['GET'])
def request_status(request_id):
    if request_id not in pending_requests:
        return jsonify({"success": False, "error": "Solicitação não encontrada"}), 404
    
    request_data = pending_requests[request_id]
    
    response = {
        "success": True,
        "status": request_data['status'],
        "author_email": request_data['author_email']
    }
    
    if request_data['status'] == 'completed' and 'result' in request_data:
        response.update(request_data['result'])
    
    return jsonify(response)

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state or state not in pending_authorizations:
        logger.error(f"Autorização inválida: code={code}, state={state}")
        return render_template_string("""
            <html>
                <body>
                    <h1>Erro na Autorização</h1>
                    <p>Ocorreu um erro no processo de autorização.</p>
                </body>
            </html>
        """)

    pending_authorizations[state]['code'] = code
    pending_authorizations[state]['completed'] = True
    
    return render_template_string("""
        <html>
            <body>
                <h1>Autorização Concluída com Sucesso!</h1>
                <p>Você pode fechar esta janela agora.</p>
            </body>
        </html>
    """)

def register_authorization_for_request(request_id):
    state = str(uuid.uuid4())
    pending_authorizations[state] = {
        'request_id': request_id,
        'code': None,
        'completed': False,
        'timestamp': datetime.datetime.now()
    }
    return state

def wait_for_authorization(state, timeout=300):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if state in pending_authorizations and pending_authorizations[state]['completed']:
            return pending_authorizations[state]['code']
        time.sleep(1)
    
    if state in pending_authorizations:
        del pending_authorizations[state]
    return None

orcid_authorization = OrcidAuthorization(
    orcid_client, 
    email_sender,
    register_authorization_func=register_authorization_for_request,
    wait_for_authorization_func=wait_for_authorization
)

def process_authorization(request_id):
    request_data = pending_requests[request_id]
    
    result = orcid_authorization.process_authorization(
        author_email=request_data['author_email'],
        author_name=request_data['author_name'],
        work_data=request_data['work_data'],
        storage_path=f"author_token_{request_id}.json",
        request_id=request_id
    )
    
    pending_requests[request_id]['status'] = 'completed' if result['success'] else 'failed'
    pending_requests[request_id]['result'] = result

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5100)