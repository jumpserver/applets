import os
import sys

APPDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.append(APPDIR)


class BaseConfig:
    """base config"""
    DEBUG = False
    TESTING = False
    APPDIR = APPDIR
    SETUP_FILE = 'setup.yml'
    MANIFEST_FILE = 'manifest.yml'
    PLATFORM_FILE = 'platform.yml'
    CONFIG_FILES = [SETUP_FILE, MANIFEST_FILE, PLATFORM_FILE]


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):
    pass


config = {
    'default': DevelopmentConfig, 
    'development': DevelopmentConfig, 
    'testing': TestingConfig,
    'production': ProductionConfig,
}

ENV = os.getenv('ENV', 'default')
CONFIG = config.get(ENV, )
