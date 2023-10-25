import sys
import logging
from pathlib import Path  # Python 3.6+ only
from db.mongo import MongoDBClass
from dotenv import load_dotenv


# Logger
def configure_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = configure_logging()


# Environment
logger.info("Reading .env file")
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


logger.info("Connecting to MongoDB")
mongodb = MongoDBClass()
