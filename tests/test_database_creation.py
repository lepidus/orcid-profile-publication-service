import unittest
import os
from app import app, db
from config_test import TestConfig
from models import PendingRequest, PendingAuthorization
from sqlalchemy import inspect

class TestDatabaseCreation(unittest.TestCase):
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
            self.assertIn('pending_authorizations', tables)
            
    def test_create_pending_request(self):
        with app.app_context():
            request = PendingRequest(
                request_id='test-123',
                author_email='test@example.com',
                author_name='Test Author',
                status='processing',
                work_data='{"title": "Test Work"}'
            )
            db.session.add(request)
            db.session.commit()
            
            saved_request = db.session.get(PendingRequest, 'test-123')
            self.assertIsNotNone(saved_request)
            self.assertEqual(saved_request.author_email, 'test@example.com')

if __name__ == '__main__':
    unittest.main()