# ORM для ORM, афигенно:)
from os import getenv

import pymongo
from dotenv import load_dotenv

from logg.logger import logger


load_dotenv('.env')


try:
    client = pymongo.MongoClient(getenv('mongo_connect'), connect=True)
    collection = client.LemurietsDB.MyDB
except Exception:
    logger.error('Не удалось подключиться к базе данных :/')
