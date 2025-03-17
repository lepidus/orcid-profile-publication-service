import time
import logging
import json
import os

logger = logging.getLogger(__name__)

class OrcidAuthorization:
    def __init__(self, orcid_client, email_sender, register_authorization_func, wait_for_authorization_func):
        self.orcid_client = orcid_client
        self.email_sender = email_sender
        self.register_authorization = register_authorization_func
        self.wait_for_authorization = wait_for_authorization_func
    
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
            
            state = self.register_authorization(request_id)
            
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
            
            auth_code = self.wait_for_authorization(state, timeout=300)
            
            if not auth_code:
                return {
                    "success": True,
                    "status": "awaiting_authorization", 
                    "message": f"Email enviado para {author_email}. Aguardando autorização"
                }
                
            try:
                token_response = self.orcid_client.get_token(auth_code)
                access_token = token_response.get('access_token')
                orcid_id = token_response.get('orcid')
                
                if storage_path:
                    with open(storage_path, 'w') as file:
                        json.dump(token_response, file)
            except Exception as e:
                logger.error(f"Erro ao obter token: {str(e)}")
                return {
                    "success": False,
                    "error": f"Falha ao obter token: {str(e)}"
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