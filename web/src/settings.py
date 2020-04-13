import os

SECRET_KEY = os.environ["SECRET_KEY"]
POSTGRES_DSN = os.environ["POSTGRES_DSN"]

POSTGRESS_POOL = None
