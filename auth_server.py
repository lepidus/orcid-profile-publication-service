from flask import Flask, request, render_template_string
import threading
import uuid
import logging
import datetime
import time

logger = logging.getLogger(__name__)

class AuthServer:
    def __init__(self, host='0.0.0.0', port=5100):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.server_thread = None
        self.running = False
        
        self.pending_authorizations = {}
        
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/oauth/callback')
        def orcid_callback():
            code = request.args.get('code')
            state = request.args.get('state')
            
            if not code or not state or state not in self.pending_authorizations:
                logger.error(f"Autorização inválida: code={code}, state={state}")
                return render_template_string("""
                    <html>
                        <body>
                            <h1>Erro na Autorização</h1>
                            <p>Ocorreu um erro no processo de autorização.</p>
                        </body>
                    </html>
                """)

            self.pending_authorizations[state]['code'] = code
            self.pending_authorizations[state]['completed'] = True
            
            request_id = self.pending_authorizations[state].get('request_id')
            
            if request_id:
                pass
            
            return render_template_string("""
                <html>
                    <body>
                        <h1>Autorização Concluída com Sucesso!</h1>
                        <p>Você pode fechar esta janela agora.</p>
                    </body>
                </html>
            """)

    def register_authorization_for_request(self, request_id):
        state = str(uuid.uuid4())
        self.pending_authorizations[state] = {
            'request_id': request_id,
            'code': None,
            'completed': False,
            'timestamp': datetime.datetime.now()
        }
        return state
    
    def start(self):
        if self.running:
            return
        
        def run_app():
            self.app.run(host=self.host, port=self.port)
        
        self.server_thread = threading.Thread(target=run_app)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True
        logger.info(f"Servidor de autorização iniciado em http://{self.host}:{self.port}")
    
    def register_authorization(self):
        state = str(uuid.uuid4())
        self.pending_authorizations[state] = {
            'code': None,
            'completed': False,
            'timestamp': datetime.datetime.now()
        }
        return state
    
    def wait_for_authorization(self, state, timeout=300):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if state in self.pending_authorizations and self.pending_authorizations[state]['completed']:
                return self.pending_authorizations[state]['code']
            time.sleep(1)
        
        if state in self.pending_authorizations:
            del self.pending_authorizations[state]
        return None