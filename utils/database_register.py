from models import PendingRequest, AuthorizedAccessToken, PublishedWork
import logging
import uuid
from sqlalchemy import inspect

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseRegister():
    
    def __init__(self, database):
        self.database = database
    
    def register_pending_request(self, request_id, author_email, author_name, work_data):
        pending_request = PendingRequest(
            request_id=request_id,
            author_email=author_email,
            author_name=author_name,
            work_data=work_data
        )
        
        self.database.session.add(pending_request)
        self.database.session.commit()

        logger.info(f"Solicitação pendente registrada: {request_id}")

    def register_authorized_access_token(self, orcid_id, author_email, access_token, expiration_time):
        authorized_access_token = AuthorizedAccessToken(
            orcid_id=orcid_id,
            author_email=author_email,
            access_token=access_token,
            expiration_time=expiration_time
        )
        
        self.database.session.add(authorized_access_token)
        self.database.session.commit()
        logger.info(f"Token de acesso armazenado para: {orcid_id}")

    def register_published_work(self, external_id, put_code, orcid_id):
        published_work = PublishedWork(
            external_id=external_id,
            put_code=put_code,
            orcid_id=orcid_id
        )
        
        self.database.session.add(published_work)
        self.database.session.commit()

        logger.info(f"Trabalho salvo: external_id={external_id}, put_code={put_code}")

    def register_pending_request_state(self, request_id):
        pending_request = self.database.session.get(PendingRequest, request_id)
        state = str(uuid.uuid4())
        pending_request.set_state(state)
        self.database.session.commit()
        logger.info(f"Estado da solicitação pendente atualizado: {request_id}, state={state}")
        return pending_request.state
    
    def create_tables(self):
        inspector = inspect(self.database.engine)
        
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            logger.info("Creating database tables...")
            self.database.create_all()
        else:
            logger.info("Tables already exist, skipping creation")