from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

db = SQLAlchemy()
class PendingRequest(db.Model):
    __tablename__ = 'pending_requests'
    
    request_id = db.Column(db.String(36), primary_key=True)
    state = db.Column(db.Text, nullable=True)
    author_email = db.Column(db.String(255), nullable=False)
    author_name = db.Column(db.String(255), nullable=False)
    work_data = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    status = db.Column(db.String(50), default='processing')
    result = db.Column(db.Text, nullable=True)
    
    def set_work_data(self, work_data_dict):
        self.work_data = json.dumps(work_data_dict)
    
    def set_state(self, state):
        self.state = state
    
    def get_work_data(self):
        return json.loads(self.work_data) if self.work_data else {}
    
    def set_result(self, result_dict):
        self.result = json.dumps(result_dict) if result_dict else None
    
    def get_result(self):
        return json.loads(self.result) if self.result else {}
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'author_email': self.author_email,
            'author_name': self.author_name,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'result': self.get_result()
        }

class AuthorizedAccessToken(db.Model):
    __tablename__ = 'authorized_access_tokens'
    orcid_id = db.Column(db.String(255), primary_key=True)
    author_email = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    expiration_time = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def set_author_email(self, author_email):
        self.author_email = author_email
    
    def set_access_token(self, access_token):
        self.access_token = access_token
    
    def set_expiration_time(self, expiration_time):
        self.expiration_time = expiration_time
    
    def to_dict(self):
        return {
            'author_email': self.author_email,
            'access_token': self.access_token,
            'expiration_time': self.expiration_time,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class PublishedWork(db.Model):
    __tablename__ = 'published_works'
    external_id = db.Column(db.String(255), primary_key=True)
    orcid_id = db.Column(db.String(255), nullable=False)
    put_code = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'external_id': self.external_id,
            'orcid_id': self.orcid_id,
            'put_code': self.put_code,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }