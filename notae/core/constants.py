import os

NOTES_DIR = os.path.expanduser("~/notes")
LOGS_DIR = os.path.expanduser("~/.notae_logs")
SESSION_FILE = os.path.join(LOGS_DIR, ".notae_session")
AUTH_LOCK_FILE = os.path.join(LOGS_DIR, ".notae_lock")

# Logs solicitados no prompt
ERRORS_LOG = os.path.join(LOGS_DIR, "errors.log")
AUTH_LOG = os.path.join(LOGS_DIR, "auth_errors.log")

# Regras de Negócio
SESSION_TIMEOUT = 300  # 5 minutos
LOCKOUT_TIMEOUT = 300  # 5 minutos
MAX_AUTH_ATTEMPTS = 3
MAX_TAGS = 3

# Estrutura de arquivos
NOTE_EXTENSION = ".note"
DATE_FORMAT = "%Y%m%d%H%M%S"
