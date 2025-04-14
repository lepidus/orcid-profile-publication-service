import os
import logging
import threading
import uuid
from flask import Flask, request, jsonify, render_template_string
from utils.email_sender import EmailSender
from orcid.authorization import OrcidAuthorization
from models import db, PendingRequest, AuthorizedAccessToken, PublishedWork
from sqlalchemy import inspect
import datetime
from utils.publication_data_retrieval import PublicationDataRetrieval
from orcid_service import OrcidService
from orcid.orcid_client import OrcidClient

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
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orcid_authorizations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

orcid_client = OrcidClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
orcid_service = OrcidService(orcid_client)

email_sender = EmailSender(
    SMTP_SERVER, SMTP_PORT, 
    EMAIL_USERNAME, EMAIL_PASSWORD, 
    SENDER_EMAIL
)

@app.route('/works', methods=['POST'])
def works():
    try:
        data = request.json
        
        required_fields = ['orcid_id', 'author_email', 'author_name', 'work_data']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Campo obrigatório ausente: {field}"}), 400
        
        authorized_access_token = AuthorizedAccessToken.query.filter_by(orcid_id=data['orcid_id']).first()
        if authorized_access_token:
            return orcid_service.publish_work(data, authorized_access_token)

        request_id = str(uuid.uuid4())
        
        register_pending_request(
            request_id=request_id,
            author_email=data['author_email'],
            author_name=data['author_name'],
            work_data=data['work_data']
        )

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

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        logger.error(f"Parâmetros de autorização incompletos: code={code}, state={state}")
        return render_template_string("""
            <html>
                <body>
                    <h1>Erro na Autorização</h1>
                    <p>Parâmetros incompletos no callback.</p>
                </body>
            </html>
        """)
    
    pending_request = PendingRequest.query.filter_by(state=state).first()
    
    if not pending_request:
        logger.error(f"Autorização inválida: code={code}, state={state}")
        return render_template_string("""
            <html>
                <body>
                    <h1>Erro na Autorização</h1>
                    <p>Estado de autorização não encontrado nas requisições solicitadas.</p>
                </body>
            </html>
        """)
    
    result = orcid_authorization.process_orcid_publication(pending_request, code)
    if result['success']:
        logger.info(f"Armazenando autorização do token de acesso para: {result['orcid_id']}")
        expiration_time = datetime.datetime.now().timestamp() + result['expiration_time']

        register_authorized_access_token(
            orcid_id=result['orcid_id'],
            author_email=pending_request.author_email,
            access_token=result['access_token'],
            expiration_time=expiration_time
        )

        publication_data = PublicationDataRetrieval(pending_request.get_work_data())
        external_id = publication_data.get_external_id()
        put_code = result['put_code']

        logger.info(f"Armazenando trabalho para: {external_id}, put_code={put_code}")
        register_published_work(
            external_id=external_id,
            put_code=put_code,
            orcid_id=result['orcid_id']
        )

        logger.info(f"Removendo solicitação pendente: {pending_request.request_id}...")
        db.session.delete(pending_request)
        db.session.commit()
        return render_template_string("""
            <html>
                <body>
                    <h1>Autorização Concluída com Sucesso!</h1>
                    <p>Você pode fechar esta janela agora.</p>
                </body>
            </html>
        """)
    
    return render_template_string("""
            <html>
                <body>
                    <h1>Não conseguimos publicar na Orcid com o código de autorização fornecido</h1>
                    <p>Considere checar se a API Orcid tem permissões de publicação e verifique os erros no log do servidor.</p>
                </body>
            </html>
        """)

def register_pending_request(request_id, author_email, author_name, work_data):
    pending_request = PendingRequest(
        request_id=request_id,
        author_email=author_email,
        author_name=author_name,
        work_data=work_data
    )
    
    db.session.add(pending_request)
    db.session.commit()

    logger.info(f"Solicitação pendente registrada: {request_id}")

def register_authorized_access_token(orcid_id, author_email, access_token, expiration_time):
    authorized_access_token = AuthorizedAccessToken(
        orcid_id=orcid_id,
        author_email=author_email,
        access_token=access_token,
        expiration_time=expiration_time
    )
    
    db.session.add(authorized_access_token)
    db.session.commit()
    logger.info(f"Token de acesso armazenado para: {orcid_id}")

def register_published_work(external_id, put_code, orcid_id):
    published_work = PublishedWork(
        external_id=external_id,
        put_code=put_code,
        orcid_id=orcid_id
    )
    
    db.session.add(published_work)
    db.session.commit()

    logger.info(f"Trabalho salvo: external_id={external_id}, put_code={put_code}")

def register_pending_request_state(request_id):
    with app.app_context():
        pending_request = db.session.get(PendingRequest, request_id)
        state = str(uuid.uuid4())
        pending_request.set_state(state)
        db.session.commit()
        return pending_request.state

orcid_authorization = OrcidAuthorization(
    orcid_client, 
    email_sender,
    register_pending_request_state_func=register_pending_request_state
)

def process_authorization(request_id):
    with app.app_context():
        pending_request = PendingRequest.query.filter_by(request_id=request_id).first()
        
        if not pending_request:
            logger.error(f"Solicitação não encontrada: {request_id}")
            return
        
        result = orcid_authorization.process_authorization(
            author_email=pending_request.author_email,
            author_name=pending_request.author_name,
            work_data=pending_request.get_work_data(),
            request_id=request_id
        )
    
        pending_request.set_result(result)
        db.session.commit()

def create_tables():
    inspector = inspect(db.engine)
    
    existing_tables = inspector.get_table_names()
    
    if not existing_tables:
        logger.info("Creating database tables...")
        db.create_all()
    else:
        logger.info("Tables already exist, skipping creation")

with app.app_context():
    create_tables()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5100)