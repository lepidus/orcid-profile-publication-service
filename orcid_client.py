import requests

class OrcidClient:
    API_VERSION = "v3.0"
    BASE_URL = "https://sandbox.orcid.org/" + API_VERSION

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_url = "https://sandbox.orcid.org/oauth/token"

    def get_orcid_id_and_access_token(self, authorization_code):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri
        }

        headers = {"Accept": "application/json"}
        response = requests.post(self.token_url, data=params, headers=headers)

        return response.json()

    def publish_to_orcid(self, access_token, orcid_id, work_data):
        url = f"{self.BASE_URL}/{orcid_id}/work"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.post(url, json=work_data, headers=headers)

            if not response.content or response.status_code == 204:
                return response.status_code, {"message": "Nenhuma resposta do ORCID"}

            if response.status_code >= 400:
                return response.status_code, {"error": f"Erro {response.status_code}: {response.text}"}

            return response.status_code, response.json()

        except requests.exceptions.RequestException as e:
            return None, {"error": f"Erro na tentativa de publicar na ORCID: {str(e)}"}