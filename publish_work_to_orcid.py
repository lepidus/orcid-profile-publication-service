import os
import json
from orcid_client import OrcidClient

CLIENT_ID = os.environ.get('ORCID_CLIENT_ID')
CLIENT_SECRET = os.environ.get('ORCID_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('ORCID_REDIRECT_URL')

with open('work_data_example.json', 'r') as file:
    work_data = json.load(file)

    orcid_client = OrcidClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    print("\nPara obter seu código de autorização, acesse:\n")
    print(
        f"https://sandbox.orcid.org/oauth/authorize?client_id={CLIENT_ID}&response_type=code&scope=/activities/update&redirect_uri={REDIRECT_URI}"
    )
    auth_code = input("\nInsira o código de autorização do ORCID: ")

    print("\nObtendo Access Token...")
    token_info = orcid_client.get_orcid_id_and_access_token(auth_code)

    if "access_token" not in token_info:
        print("\nErro ao obter Access Token! Verifique suas credenciais.")
        exit()

    access_token = token_info["access_token"]
    orcid_id = token_info["orcid"]

    print(f"Access Token obtido: {access_token}")
    print(f"ORCID ID: {orcid_id}")

    print("\nPublicando trabalho no ORCID...")
    status, response = orcid_client.publish_to_orcid(access_token, orcid_id, work_data)

    if status == 201:
        print("\nTrabalho publicado com sucesso!")
    else:
        print("\nFalha ao publicar trabalho!")
        print("Resposta da API:", response)