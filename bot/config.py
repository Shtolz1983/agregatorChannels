from dotenv import load_dotenv, find_dotenv
from os import getenv


load_dotenv(find_dotenv())

API_ID = getenv('API_ID')
API_HASH = getenv('API_HASH')
SESSION_STRING = getenv('SESSION_STRING')
REDIS_HOST = getenv('REDIS_HOST')
