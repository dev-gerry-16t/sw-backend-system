from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()

mongo_host = os.getenv("MONGO_HOST") or "mongodb://localhost:27017/"

conn = MongoClient(mongo_host)

mongo_db = os.getenv("MONGO_DB") or "test"

db = conn[mongo_db]
