# Biblioteca para publicações na Orcid.org

Permite a publicação no perfil ORCID de autores utilizando a API de membro da ORCID.

## Visão geral

Essa biblioteca fornece:
- Publicação no perfil ORCID
- Fluxo de autorização OAuth2 via e-mail
- Persistência do identificador da publicação e tokens de acesso autorizados

## Requisitos

Se optar por criar seu ambiente baseado em Docker, considere somente o servidor SMTP e as credenciais API ORCID de membro. As dependências relevantes estão listadas no arquivo [requirements.txt](https://gitlab.lepidus.com.br/softwares-pkp/ferramentas-scielo/orcid-push-library/-/blob/main/requirements.txt?ref_type=heads).

- Python 3
- requests
- Flask
- gunicorn (utilizamos em produção)
- flask-sqlalchemy
- Servidor SMTP para envio de e-mails
- Credenciais de API de membro ORCID

## Como configurar

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

3. Disponibilize a aplicação na web em um domínio compatível com sua API ORCID. 

## Uso da API

Adicionar/Atualizar publicação

```http
  POST /works
```

Exemplo de requisição:

```sh
curl -X POST https://localhost:5100/works \
-H "Content-Type: application/json" \
-d '{
    "orcid_id": "0000-0002-1825-0097",
    "author_email": "author@example.com",
    "author_name": "Author Name",
    "work_data": {
        "title": {
            "title": {"value": "Publication Title"},
            "subtitle": {"value": "Publication Subtitle"}
        },
        "journal-title": {"value": "Journal Name"},
        "type": "journal-article",
        "external-ids": {
            "external-id": [{
                "external-id-type": "doi",
                "external-id-value": "10.1000/example.123",
                "external-id-url": {"value": "https://doi.org/10.1000/example.123"}
            }]
        },
        "publication-date": {
            "year": {"value": "2025"},
            "month": {"value": "03"},
            "day": {"value": "17"}
        }
    }
}'
```

| Parâmetro no corpo da requisição   | Tipo       | Descrição                           |
| :---------- | :--------- | :---------------------------------- |
| `orcid_id` | `string` | **Obrigatório**. O identificador ORCID do autor (formato: XXXX-XXXX-XXXX-XXXX) |
| `author_email` | `string` | **Obrigatório**. Email do autor para envio do link de autorização |
| `author_name` | `string` | **Obrigatório**. Nome completo do autor para personalização do email |
| `work_data` | `object` | **Obrigatório**. Objeto contendo os detalhes da publicação |
| `work_data.title.title.value` | `string` | **Obrigatório**. Título principal da publicação |
| `work_data.title.subtitle.value` | `string` | Subtítulo da publicação (opcional) |
| `work_data.journal-title.value` | `string` | **Obrigatório**. Nome do periódico onde o trabalho foi publicado |
| `work_data.type` | `string` | **Obrigatório**. Tipo do trabalho (ex: journal-article, book-chapter) |
| `work_data.external-ids` | `object` | **Obrigatório**. Identificadores externos da publicação |
| `work_data.external-ids.external-id` | `array` | Lista de identificadores externos |
| `work_data.external-ids.external-id[].external-id-type` | `string` | Tipo do identificador externo (ex: doi, issn) |
| `work_data.external-ids.external-id[].external-id-value` | `string` | Valor do identificador externo |
| `work_data.external-ids.external-id[].external-id-url.value` | `string` | URL associada ao identificador externo |
| `work_data.publication-date.year.value` | `string` | **Obrigatório**. Ano de publicação |
| `work_data.publication-date.month.value` | `string` | Mês de publicação (opcional) |
| `work_data.publication-date.day.value` | `string` | Dia de publicação (opcional) |