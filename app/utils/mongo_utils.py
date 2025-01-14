from pymongo import MongoClient

from config import Config


class MongoDB:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]

    def get_collection(self, collection_name):
        return self.db[collection_name]


mongo_client = MongoDB()
