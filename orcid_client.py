import requests

class OrcidClient:
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