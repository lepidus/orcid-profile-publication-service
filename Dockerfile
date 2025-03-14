FROM python:3.12-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_RUN_HOST=0.0.0.0
ENV SMTP_SERVER=mailpit
ENV SMTP_PORT=1025

EXPOSE 5100

CMD ["python", "app.py"]