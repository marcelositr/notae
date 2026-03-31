import os
import re
import unicodedata
import logging
from datetime import datetime
from notae.core.constants import NOTES_DIR, LOGS_DIR, ERRORS_LOG, AUTH_LOG

def setup_directories():
    os.makedirs(NOTES_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Simple setup for internal logging
    logging.basicConfig(level=logging.INFO)
    
    error_logger = logging.getLogger("notae_errors")
    error_logger.setLevel(logging.ERROR)
    err_handler = logging.FileHandler(ERRORS_LOG)
    err_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    error_logger.addHandler(err_handler)

    auth_logger = logging.getLogger("notae_auth")
    auth_logger.setLevel(logging.INFO)
    auth_handler = logging.FileHandler(AUTH_LOG)
    auth_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    auth_logger.addHandler(auth_handler)

    return error_logger, auth_logger

def sanitize_filename(title):
    # Normalize unicode characters to remove accents
    nfkd_form = unicodedata.normalize('NFKD', title)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    
    # Lowercase and replace spaces with underscore
    sanitized = only_ascii.lower().replace(' ', '_')
    
    # Remove everything except lowercase letters, numbers, and underscores
    # (The rule says "Remover acentos e caracteres especiais")
    # I'll keep underscores as they are used for spaces.
    sanitized = re.sub(r'[^a-z0-9_]', '', sanitized)
    
    # Remove redundant underscores
    sanitized = re.sub(r'_+', '_', sanitized).strip('_')
    
    return sanitized

def get_now():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def log_error(msg):
    _, error_logger = setup_logging_lazy()
    error_logger.error(msg)

def log_auth(msg):
    auth_logger, _ = setup_logging_lazy()
    auth_logger.info(msg)

_loggers = None
def setup_logging_lazy():
    global _loggers
    if _loggers is None:
        error_logger, auth_logger = setup_logging()
        _loggers = (auth_logger, error_logger)
    return _loggers
