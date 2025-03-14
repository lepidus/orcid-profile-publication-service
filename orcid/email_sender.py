import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, smtp_server, smtp_port, username=None, password=None, sender_email=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = sender_email or "noreply@exemplo.com"
    
    def send_authorization_email(self, recipient_email, author_name, auth_url):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "Autorização para adicionar publicação ao seu perfil ORCID"
            
            body = f"""
            <html>
                <body>
                    <p>Prezado(a) {author_name},</p>
                    <p>Clique no link para autorizar: <a href="{auth_url}">{auth_url}</a></p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.username and self.password:
                server.starttls()
                server.login(self.username, self.password)
                
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email de autorização enviado para {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False