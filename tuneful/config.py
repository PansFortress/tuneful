class DevelopmentConfig(object):
    DATABASE_URI = "postgresql:///tuneful"
    DEBUG = True
    UPLOAD_FOLDER = "uploads"

class TestingConfig(object):
    DATABASE_URI = "postgresql:///tuneful-test"
    DEBUG = True
    UPLOAD_FOLDER = "test-uploads"
    # SERVER_NAME = "test_server"
