import time
import logging
import json
import os

logger = logging.getLogger(__name__)

class OrcidAuthorization:
    def __init__(self, orcid_client, auth_server, email_sender):
        self.orcid_client = orcid_client
        self.auth_server = auth_server
        self.email_sender = email_sender
        
        if not auth_server.running:
            auth_server.start()
    
    def process_authorization(self, author_email, author_name, work_data, storage_path=None, request_id=None):
        access_token = None
        orcid_id = None
        
        if storage_path and os.path.exists(storage_path):
            try:
                with open(storage_path, 'r') as file:
                    stored_data = json.load(file)
                    
                    if ("access_token" in stored_data and 
                        "scope" in stored_data and 
                        "expires_in" in stored_data):
                        
                        if self.orcid_client.is_authorized_access_token(
                                stored_data["scope"], 
                                stored_data["expires_in"]):
                            
                            access_token = stored_data["access_token"]
                            orcid_id = stored_data.get("orcid")
                            logger.info("Token válido encontrado no armazenamento")
            except Exception as e:
                logger.error(f"Erro ao ler arquivo de armazenamento: {str(e)}")
        
        if not access_token:
            logger.info("Iniciando processo de autorização")
            
            if request_id:
                state = self.auth_server.register_authorization_for_request(request_id)
            else:
                state = self.auth_server.register_authorization()
            
            auth_url = f"{self.orcid_client.get_auth_url()}&state={state}"
            
            email_sent = self.email_sender.send_authorization_email(
                author_email, 
                author_name, 
                auth_url
            )
            
            if not email_sent:
                logger.error("Falha ao enviar email de autorização")
                return {
                    "success": False,
                    "error": "Falha ao enviar email de autorização"
                }
            
            logger.info(f"Email enviado para {author_email}. Aguardando autorização...")
            
            return {
                "success": True,
                "status": "awaiting_authorization", 
                "message": f"Email enviado para {author_email}. Aguardando autorização"
            }
            
        logger.info(f"Publicando trabalho para ORCID ID: {orcid_id}")
        status, response = self.orcid_client.publish_to_orcid(access_token, orcid_id, work_data)
        
        if status == 201:
            logger.info("Trabalho publicado com sucesso!")
            return {
                "success": True,
                "orcid_id": orcid_id,
                "message": "Trabalho publicado com sucesso"
            }
        else:
            logger.error(f"Falha ao publicar trabalho: {response}")
            return {
                "success": False,
                "error": f"Falha ao publicar trabalho: {response}"
            }