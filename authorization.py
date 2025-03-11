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
    
    def process_authorization(self, author_email, author_name, work_data, storage_path=None):
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
            
            auth_code = self.auth_server.wait_for_authorization(state, timeout=300)
            
            if not auth_code:
                logger.error("Timeout de autorização atingido")
                return {
                    "success": False,
                    "error": "Tempo limite para autorização excedido"
                }
            
            logger.info("Código de autorização recebido")
            
            token_info = self.orcid_client.get_orcid_id_and_access_token(auth_code)
            
            if "error" in token_info or "access_token" not in token_info:
                logger.error(f"Erro ao obter token: {token_info.get('error', 'Erro desconhecido')}")
                return {
                    "success": False,
                    "error": token_info.get("error", "Falha ao obter token de acesso")
                }
            
            access_token = token_info["access_token"]
            orcid_id = token_info["orcid"]
            
            if storage_path:
                try:
                    with open(storage_path, 'w') as file:
                        expires_at = int(time.time()) + token_info.get("expires_in", 3600)
                        
                        storage_data = {
                            "access_token": access_token,
                            "refresh_token": token_info.get("refresh_token"),
                            "orcid": orcid_id,
                            "scope": token_info.get("scope"),
                            "expires_in": expires_at
                        }
                        
                        json.dump(storage_data, file, indent=2)
                        logger.info(f"Dados de token armazenados em {storage_path}")
                except Exception as e:
                    logger.error(f"Erro ao armazenar token: {str(e)}")
        
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