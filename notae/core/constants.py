import os

NOTES_DIR = os.path.expanduser("~/notes")
LOGS_DIR = os.path.expanduser("~/.notae_logs")
SESSION_FILE = os.path.join(LOGS_DIR, ".notae_session")
AUTH_LOCK_FILE = os.path.join(LOGS_DIR, ".notae_lock")

# Logs
ERRORS_LOG = os.path.join(LOGS_DIR, "errors.log")
AUTH_LOG = os.path.join(LOGS_DIR, "auth.log")

# Constraints
SESSION_TIMEOUT = 300  # 5 minutes in seconds
LOCKOUT_TIMEOUT = 300  # 5 minutes in seconds
MAX_AUTH_ATTEMPTS = 3
MAX_TAGS = 3

# File structure
NOTE_EXTENSION = ".note"
DATE_FORMAT = "%Y%m%d-%H%M%S"
