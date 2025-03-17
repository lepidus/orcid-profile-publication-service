FROM python:3.12-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_RUN_HOST=0.0.0.0
ENV SMTP_SERVER=mailpit
ENV SMTP_PORT=1025

RUN mkdir -p /data && chown -R 1000:1000 /data
ENV SQLALCHEMY_DATABASE_URI=sqlite:////data/orcid_authorizations.db

VOLUME ["/data"]
EXPOSE 5100

CMD ["python", "app.py"]