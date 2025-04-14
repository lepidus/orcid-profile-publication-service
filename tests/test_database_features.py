import unittest
import os
from app import app, db
from config_test import TestConfig
from models import PendingRequest, AuthorizedAccessToken, PublishedWork
from sqlalchemy import inspect
import uuid

class TestDatabaseFeatures(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
            
    def test_tables_exist(self):
        with app.app_context():
            inspection = inspect(db.engine)
            tables = inspection.get_table_names()
            self.assertIn('pending_requests', tables)
            self.assertIn('authorized_access_tokens', tables)
            self.assertIn('published_works', tables)
            
    def test_create_pending_request(self):
        with app.app_context():
            self.create_pending_request_for_testing()
            saved_request = db.session.get(PendingRequest, 'test-123')
            self.assertIsNotNone(saved_request)
            self.assertEqual(saved_request.author_email, 'test@example.com')
    
    def test_add_pending_request_state_id(self):
        with app.app_context():
            self.create_pending_request_for_testing()
            state = str(uuid.uuid4())
            request = db.session.get(PendingRequest, 'test-123')
            request.set_state(state)
            db.session.commit()
            self.assertEqual(request.state, state)
    
    def test_create_authorized_access_token(self):
        with app.app_context():
            self.create_authorized_access_token()
            saved_authorized_access_token = db.session.get(AuthorizedAccessToken, 'test-orcid-id')
            self.assertIsNotNone(saved_authorized_access_token)
            self.assertEqual(saved_authorized_access_token.orcid_id, 'test-orcid-id')
    
    def test_authorized_access_token_update(self):
        with app.app_context():
            self.create_authorized_access_token()
            saved_authorized_access_token = db.session.get(AuthorizedAccessToken, 'test-orcid-id')
            saved_authorized_access_token.set_author_email('test@mailinator.com')
            saved_authorized_access_token.set_access_token('new-token')
            saved_authorized_access_token.set_expiration_time(7200)
            db.session.commit()
            self.assertIsNotNone(saved_authorized_access_token)
            self.assertEqual(saved_authorized_access_token.author_email, 'test@mailinator.com')
            self.assertEqual(saved_authorized_access_token.access_token, 'new-token')
            self.assertEqual(saved_authorized_access_token.expiration_time, 7200)
    
    def test_create_published_work(self):
        with app.app_context():
            self.create_published_work()
            saved_published_work = db.session.get(PublishedWork, 'test-123')
            self.assertIsNotNone(saved_published_work)
            self.assertEqual(saved_published_work.put_code, 'test-put-code')
    
    def test_published_work_update(self):
        with app.app_context():
            self.create_published_work()
            saved_published_work = db.session.get(PublishedWork, 'test-123')
            saved_published_work.set_put_code('123456')
            db.session.commit()
            self.assertIsNotNone(saved_published_work)
            self.assertEqual(saved_published_work.put_code, '123456')

    def create_pending_request_for_testing(self):
        request = PendingRequest(
            request_id='test-123',
            author_email='test@example.com',
            author_name='Test Author',
            work_data='{"title": "Test Work"}'
        )
        db.session.add(request)
        db.session.commit()
    
    def create_authorized_access_token(self):
        authorized_access_token = AuthorizedAccessToken(
            orcid_id='test-orcid-id',
            author_email='test@example.com',
            access_token='test-token',
            expiration_time=3600
        )
        db.session.add(authorized_access_token)
        db.session.commit()
    
    def create_published_work(self):
        published_work = PublishedWork(
            external_id='test-123',
            orcid_id='test-orcid-id',
            put_code='test-put-code'
        )
        db.session.add(published_work)
        db.session.commit()

if __name__ == '__main__':
    unittest.main()