
from models import db, PublishedWork
import logging
from utils.publication_data_retrieval import PublicationDataRetrieval

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrcidService():
    def __init__(self, orcid_client):
        self.orcid_client = orcid_client

    def publish_work(self, data, authorized_access_token):
        if self.orcid_client.is_authorized_access_token(authorized_access_token.expiration_time):
            logger.info(f"O autor {data['author_email']} já autorizou SciELO Brasil para publicar em seu Orcid.")
            publication_data_retrieval = PublicationDataRetrieval(data['work_data'])
            external_id = publication_data_retrieval.get_external_id()
            published_work = PublishedWork.query.filter_by(external_id=external_id, orcid_id=data['orcid_id']).first()
            if published_work:
                logger.info(f"O trabalho já foi publicado anteriormente. External id: {published_work.external_id}. Iniciando processo de atualização.")

                status, response = self.orcid_client.publish_to_orcid(authorized_access_token.access_token, data['orcid_id'], data['work_data'], published_work)
                if status == 200:
                    logger.info("Trabalho atualizado com sucesso!")
                    
                    return {
                        "success": True,
                        "orcid_id": authorized_access_token.orcid_id,
                        "message": "Trabalho atualizado com sucesso"
                    }
                else:
                    logger.error(f"Falha ao atualizar trabalho: {response}")
                    return {
                        "success": False,
                        "error": f"Falha ao atualizar trabalho: {response}"
                    }
            else:
                status, response = self.orcid_client.publish_to_orcid(authorized_access_token.access_token, data['orcid_id'], data['work_data'])
                if status == 201:
                    logger.info("Trabalho publicado com sucesso!")
                    
                    return {
                        "success": True,
                        "orcid_id": authorized_access_token.orcid_id,
                        "message": "Trabalho publicado com sucesso",
                        "put_code": response['put-code']
                    }
                else:
                    logger.error(f"Falha ao publicar trabalho: {response}")
                    return {
                        "success": False,
                        "error": f"Falha ao publicar trabalho: {response}"
                    }
        else:
            logger.info(f"Token expirado encontrado para {data['author_email']}")
            db.session.delete(authorized_access_token)
            db.session.commit()
            logger.info(f"Token expirado removido para {data['author_email']}")