from .base import *

DEBUG = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'production.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'uploader': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        }
    },
}


TUS_UPLOAD_DIR = os.path.join('/upload', 'tmp')
TUS_DESTINATION_DIR = os.path.join('/upload', 'hguploads')
TUS_FILE_NAME_FORMAT = 'random-suffix'

