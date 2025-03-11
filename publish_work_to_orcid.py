import os
import json
import logging
from orcid_client import OrcidClient
from auth_server import AuthServer
from email_sender import EmailSender
from authorization import OrcidAuthorization

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

CLIENT_ID = os.environ.get('ORCID_CLIENT_ID')
CLIENT_SECRET = os.environ.get('ORCID_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:5000/orcid/callback"

SMTP_SERVER = "localhost"
SMTP_PORT = 1025 
EMAIL_USERNAME = ""
EMAIL_PASSWORD = ""
SENDER_EMAIL = "desenvlepidus@mailinator.com"

def main():
    with open('work_data_example.json', 'r') as file:
        work_data = json.load(file)
    print(CLIENT_ID)

    orcid_client = OrcidClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    auth_server = AuthServer(host='localhost', port=5000)
    email_sender = EmailSender(
        SMTP_SERVER, SMTP_PORT, 
        EMAIL_USERNAME, EMAIL_PASSWORD, 
        SENDER_EMAIL
    )
    
    auth_server.start()
    
    authorization = OrcidAuthorization(orcid_client, auth_server, email_sender)
    
    result = authorization.process_authorization(
        author_email="scielo_desenv@mailinator.com",
        author_name="Nome do Autor",
        work_data=work_data,
        storage_path="author_token.json"
    )
    
    if result["success"]:
        print(f"Sucesso! Trabalho publicado no ORCID {result['orcid_id']}")
    else:
        print(f"Erro: {result['error']}")

if __name__ == "__main__":
    main()