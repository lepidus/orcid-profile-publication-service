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
curl -X POST https://your_domain.com/works \
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

## Fluxo de publicação no perfil ORCID

A biblioteca funciona em dois cenários distintos:

- **Quando é a primeira solicitação de publicação de um autor (sem autorização prévia).**

1. A biblioteca recebe uma requisição POST no endpoint /works, com os parâmetros relevantes no corpo da requisição (ex: ORCID ID, e-mail do autor, título, periódico etc.).
2. Valida os dados e verifica se o autor já autorizou publicações.
3. Como não há autorização, a biblioteca envia um e-mail com o link de autorização e armazena a requisição como pendente.
4. Quando o autor autoriza, o ORCID envia um código para o endpoint /oauth/callback.
5. A biblioteca usa esse código para obter o token de acesso e fazer a publicação no ORCID.
6. O token é armazenado vinculado ao ORCID ID do autor, para futuras publicações.

- **Quando o autor já autorizou previamente.**

1. A biblioteca recebe uma requisição POST no endpoint /works.
2. Valida os dados e confirma a autorização existente.
3. Utiliza o token de acesso previamente armazenado para publicar diretamente no ORCID.

- **Diagrama de sequência**

![texto alternativo](https://i.imgur.com/qQvSanS.png)

## Ambiente de desenvolvimento

É possível montar um ambiente de desenvolvimento da biblioteca utilizando o docker-compose-local.yml, que disponibiliza a biblioteca em `http://localhost:5100`e o mailpit em `http://localhost:8025/`. É importante ressaltar que: não conseguimos fazer autorização em ambiente local. O redirecionamento da ORCID espera um domínio público e compatível com suas credenciais ORCID, nesse caso, é importante que o ambiente de teste esteja disponível e acessível para a ORCID sandbox redirecionar autorizações.

- **Executar testes automatizados:**

```bash
python -m unittest discover -s tests/ -p "*.py" -v
```

## Estrutura do projeto

```
├── app.py                           # Aplicação principal Flask com as rotas e configurações
├── docker-compose-local.yml         # Configuração Docker para ambiente de desenvolvimento
├── docker-compose.yml              # Configuração Docker para ambiente de produção
├── Dockerfile                      # Instruções para construir a imagem Docker
├── models.py                       # Modelos SQLAlchemy para o banco de dados
├── orcid/                         # Módulo com funcionalidades específicas da ORCID
│   ├── authorization.py           # Gerencia o fluxo de autorização OAuth2
│   ├── orcid_client.py           # Cliente para comunicação com a API ORCID
│   ├── orcid_service.py          # Serviço de alto nível para operações ORCID
├── README.md                      # Documentação do projeto
├── requirements.txt               # Dependências Python necessárias
├── tests/                        # Diretório de testes automatizados
│   ├── config_test.py            # Configurações para ambiente de teste
│   ├── test_database_features.py # Testes das funcionalidades do banco de dados
│   ├── test_orcid_client.py      # Testes do cliente ORCID
│   └── test_publication_data_retrieval.py  # Testes do processamento de dados
└── utils/                        # Módulo com utilitários gerais
    ├── database_register.py      # Gerenciamento de registros no banco de dados
    ├── email_sender.py           # Serviço de envio de emails
    ├── publication_data_retrieval.py  # Processamento de dados das publicações
```

## Créditos

## Licença