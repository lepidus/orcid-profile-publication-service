# Biblioteca para publicações na Orcid.org

Permite a publicação no perfil ORCID de autores utilizando a API de membro da ORCID.

## Visão geral

Essa biblioteca fornece:
- Publicação no perfil ORCID
- Fluxo de autorização OAuth2 via e-mail
- Persistência do identificador da publicação e tokens de acesso autorizados

## Requisitos

Se optar por criar seu ambiente baseado em Docker, considere somente o último item (credenciais ORCID). As dependências relevantes estão listadas no arquivo [requirements.txt](https://gitlab.lepidus.com.br/softwares-pkp/ferramentas-scielo/orcid-push-library/-/blob/main/requirements.txt?ref_type=heads).

- Python 3
- requests
- Flask
- gunicorn (utilizamos em produção)
- flask-sqlalchemy
- Credenciais de API de membro ORCID

## Como utilizar

1. Clone o repositório:

```bash
git clone https://gitlab.lepidus.com.br/softwares-pkp/ferramentas-scielo/orcid-push-library.git
cd orcid-push-library
```

2. Crie um arquivo `.env`:

```properties
ORCID_CLIENT_ID=xxxxxxxxxxxxxxxxxxxx
ORCID_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxx
REDIRECT_URI=https://your-domain.com/oauth/callback
SENDER_EMAIL=your-email@domain.com
ORCID_API_BASE_URL=https://api.sandbox.orcid.org
ORCID_BASE_URL=https://sandbox.orcid.org
ORCID_API_VERSION=v3.0
ORCID_API_MEMBER_SCOPE=/activities/update
```

**Observação: certifique-se de não usar aspas nos valores das variáveis, isso pode causar problemas nas requisições para a API da ORCID.**

| Variável   | Descrição  |
| :---------- | :--------- |
| `ORCID_CLIENT_ID` | `string` |
| `ORCID_CLIENT_ID` | `string` |
