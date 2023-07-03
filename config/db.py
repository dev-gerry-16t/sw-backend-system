from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_host = os.getenv("MONGO_HOST")

conn = MongoClient(mongo_host)

mongo_db = os.getenv("MONGO_DB")

db = conn[mongo_db]