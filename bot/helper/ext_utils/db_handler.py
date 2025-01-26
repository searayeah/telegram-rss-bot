from loguru import logger
from pymongo import MongoClient


class MongoDB:
    def __init__(
        self,
        uri: str = "mongodb://root:example@localhost:27017/",
        db_name: str = "seara_rss_config",
        collection_name: str = "subreddits",
    ) -> None:
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

    def connect(self) -> None:
        if not self.client:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"Connected to database: {self.db_name}")
            logger.info(f"Using collection: {self.collection_name}")

    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
            logger.info("Disconnected from the database.")

    def create_subreddits_table(self, data: dict) -> None:
        if self.collection is None:
            raise Exception("Not connected to the database.")

        if self.collection.count_documents({}) == 0:
            self.collection.insert_many(data)
            logger.info("Collection subreddits inserted.")
        else:
            logger.info("Collection already exists")

    def remove_subreddit(self, data: dict) -> None:
        if self.collection is None:
            raise Exception("Not connected to the database.")

        result = self.collection.delete_one(
            {"name": data["name"], "period": data["period"]}
        )

        if result.deleted_count > 0:
            logger.info(
                f"Subreddit '{data["name"]}' with period '{data["period"]}' removed."
            )
        else:
            logger.info(
                f"Subreddit '{data["name"]}' with period '{data["period"]}' not found."
            )

    def update_subreddit(self, data: dict) -> None:
        if self.collection is None:
            raise Exception("Not connected to the database.")

        result = self.collection.update_one(
            {"name": data["name"], "period": data["period"]}, {"$set": data}, upsert=True
        )

        if result.matched_count > 0:
            logger.info(
                f"Subreddit '{data["name"]}' with period '{data["period"]}' updated."
            )
        else:
            logger.info(
                f"Subreddit '{data["name"]}' with period '{data["period"]}' not found."
            )

    def get_all_subreddits(self) -> dict:
        if self.collection is None:
            raise Exception("Not connected to the database.")

        subreddits = list(self.collection.find())
        logger.info(f"Retrieved {len(subreddits)} subreddits.")
        return subreddits


database = MongoDB()
