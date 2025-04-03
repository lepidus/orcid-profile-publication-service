import time
import logging
import json
import os
from orcid.publication_data_retrieval import PublicationDataRetrieval

logger = logging.getLogger(__name__)

class OrcidAuthorization:
    def __init__(self, orcid_client, email_sender, register_authorization_func):
        self.orcid_client = orcid_client
        self.email_sender = email_sender
        self.register_authorization = register_authorization_func
    
    def process_authorization(self, author_email, author_name, work_data, storage_path=None, request_id=None):
        access_token = None
        
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
                            logger.info("Token válido encontrado no armazenamento")
                            return self.process_orcid_publication(
                                request_id, 
                                access_token
                            ) 
            except Exception as e:
                logger.error(f"Erro ao ler arquivo de armazenamento: {str(e)}")
        
        if not access_token:
            logger.info("Iniciando processo de autorização")
            
            state = self.register_authorization(request_id)
            
            auth_url = f"{self.orcid_client.get_auth_url()}&state={state}"
            
            publication_data_retrieval = PublicationDataRetrieval(work_data)
            email_sent = self.email_sender.send_authorization_email(
                author_email, 
                author_name,
                publication_data_retrieval.get_publication_title(),
                publication_data_retrieval.get_journal_title(),
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
    
    def process_orcid_publication(self, pending_request, auth_code):
        try:
            token_response = self.orcid_client.get_orcid_id_and_access_token(auth_code)
            access_token = token_response.get('access_token')
            orcid_id = token_response.get('orcid')
        except Exception as e:
            logger.error(f"Erro ao obter token: {str(e)}")
            return {
                "success": False,
                "error": f"Falha ao obter token: {str(e)}"
            }
        
        logger.info(f"Publicando trabalho para ORCID ID: {orcid_id}")
        status, response = self.orcid_client.publish_to_orcid(access_token, orcid_id, pending_request.get_work_data())
        
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