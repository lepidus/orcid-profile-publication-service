import os
import logging
import threading
import uuid
import time
from flask import Flask, request, jsonify
from orcid_client import OrcidClient
from email_sender import EmailSender 
from authorization import OrcidAuthorization
from auth_server import AuthServer

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

orcid_client = OrcidClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
auth_server = AuthServer(host='localhost', port=5100)
email_sender = EmailSender(
    SMTP_SERVER, SMTP_PORT, 
    EMAIL_USERNAME, EMAIL_PASSWORD, 
    SENDER_EMAIL
)

auth_server.start()

def process_authorization(request_id):
    request_data = pending_requests[request_id]
    
    authorization = OrcidAuthorization(orcid_client, auth_server, email_sender)
    
    result = authorization.process_authorization(
        author_email=request_data['author_email'],
        author_name=request_data['author_name'],
        work_data=request_data['work_data'],
        storage_path=f"author_token_{request_id}.json",
        request_id=request_id
    )
    
    pending_requests[request_id]['status'] = 'completed' if result['success'] else 'failed'
    pending_requests[request_id]['result'] = result

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5100)