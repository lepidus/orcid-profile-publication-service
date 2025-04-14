import requests
import datetime
import logging
import os

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
class OrcidClient:
    API_BASE_URL = os.environ.get('ORCID_API_BASE_URL') + "/" + os.environ.get('ORCID_API_VERSION')
    BASE_URL = os.environ.get('ORCID_BASE_URL')
    ORCID_API_MEMBER_SCOPE = os.environ.get('ORCID_API_MEMBER_SCOPE')

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_url = f"{os.environ.get('ORCID_API_BASE_URL')}/oauth/token"
    
    def is_authorized_access_token(self, expiration_time):
        if not expiration_time:
            return False
            
        current_time = datetime.datetime.now().timestamp()

        buffer_time = 300  
        return current_time + buffer_time < expiration_time
    
    def get_auth_url(self):
        return (f"{self.BASE_URL}/oauth/authorize?client_id={self.client_id}"
                f"&response_type=code&scope={self.ORCID_API_MEMBER_SCOPE}"
                f"&redirect_uri={self.redirect_uri}")
    
    def get_orcid_id_and_access_token(self, authorization_code):
        logger.info(f"Obtendo access token a partir do authorization code: {authorization_code}")
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri
        }
        logger.info(f"parâmetros passados para a requisição: {params}")
        headers = {"Accept": "application/json"}
        response = requests.post(self.token_url, data=params, headers=headers)
        logger.info(f"Resposta da requisição: {response.text}")

        return response.json()

    def publish_to_orcid(self, access_token, orcid_id, work_data, published_item=None):
        url = f"{self.API_BASE_URL}/{orcid_id}/work"
        if (published_item):
            url += f"/{published_item.put_code}"
            work_data['put-code'] = f"{published_item.put_code}"

        headers = {
            "Content-Type": "application/vnd.orcid+json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        try:
            if published_item:
                response = requests.put(url, json=work_data, headers=headers)
            else:
                response = requests.post(url, json=work_data, headers=headers)
                
            if not response.content or response.status_code == 204:
                return response.status_code, {"message": "Nenhuma resposta do ORCID", "put-code": response.headers['location'].split('/')[-1]}

            if response.status_code >= 400:
                return response.status_code, {"error": f"Erro {response.status_code}: {response.text}"}


            return response.status_code, response.json()

        except requests.exceptions.RequestException as e:
            return None, {"error": f"Erro na tentativa de publicar na ORCID: {str(e)}"}