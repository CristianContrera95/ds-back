import os


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 2 * 30 * 24 * 60 # = 2 months

USERS = [
    {"username": "gdmuser", "password": "laclave"},
]

API_VERSION = "api/2.0"
JOB_MAX_CONCURRENT = 10

CLIENT_TOKEN_DURATION_IN_HOURS = 1

STORAGE_CONN_STR = os.environ.get("STORAGE_CONNSTR")
FEEDBACK_CONTAINER = os.environ.get("FEEDBACK_CONTAINER")
