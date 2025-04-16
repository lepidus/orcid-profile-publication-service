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
SMTP_SERVER=xxxxxxxxxxxx
SMTP_PORT=xxxx
EMAIL_USERNAME=xxxxxxxx
EMAIL_PASSWORD=xxxxxxx
```

**Observação: certifique-se de não usar aspas nos valores das variáveis, isso pode causar problemas nas requisições para a API da ORCID.**

| Variável   | Descrição  |
| :---------- | :--------- |
| `ORCID_CLIENT_ID` | Identificador único do cliente fornecido pela ORCID para sua aplicação |
| `ORCID_CLIENT_SECRET` | Chave secreta fornecida pela ORCID para autenticar sua aplicação |
| `REDIRECT_URI` | URL para onde a ORCID redirecionará após a autorização do usuário (ex: https://domain.com.br/oauth/callback) |
| `SENDER_EMAIL` | Endereço de e-mail que será usado como remetente para enviar os e-mails de autorização |
| `ORCID_API_BASE_URL` | URL base da API ORCID (sandbox: https://api.sandbox.orcid.org, produção: https://api.orcid.org) |
| `ORCID_BASE_URL` | URL base do site ORCID (sandbox: https://sandbox.orcid.org, produção: https://orcid.org) |
| `ORCID_API_VERSION` | Versão da API ORCID a ser utilizada (atualmente v3.0) |
| `ORCID_API_MEMBER_SCOPE` | Escopo de acesso para a API de membro da ORCID (geralmente /activities/update para publicações) |
| `SMTP_SERVER` | Endereço do servidor SMTP para envio de emails (ex: smtp.gmail.com para Gmail, ou mailpit para ambiente de desenvolvimento) |
| `SMTP_PORT` | Porta do servidor SMTP (ex: 1025 para Mailpit em desenvolvimento) |
| `EMAIL_USERNAME` | Nome de usuário para autenticação no servidor SMTP |
| `EMAIL_PASSWORD` | Senha para autenticação no servidor SMTP |
