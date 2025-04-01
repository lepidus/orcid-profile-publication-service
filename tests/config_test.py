import os
import tempfile

db_fd, db_path = tempfile.mkstemp()

class TestConfig:
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True