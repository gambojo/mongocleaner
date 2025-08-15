#!/usr/bin/env python3

import os
import sys
from abc import ABC, abstractmethod
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus
from typing import Optional, Dict, Any

# ==================== Interfaces ====================
class ILogger(ABC):
    @abstractmethod
    def log(self, message: str, prefix: str = "", is_error: bool = False) -> None:
        pass

class IDBConnector(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def get_collection(self):
        pass

class ICleanStrategy(ABC):
    @abstractmethod
    def get_query(self, cutoff_date: datetime) -> Dict[str, Any]:
        pass

# ==================== Implementations ====================
class ConsoleLogger(ILogger):
    def log(self, message: str, prefix: str = "", is_error: bool = False) -> None:
        output = sys.stderr if is_error else sys.stdout
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        print(f"{timestamp} [{prefix}] {message}", file=output)

class MongoDBConnector(IDBConnector):
    def __init__(self, config: Dict[str, Any], logger: ILogger):
        self.config = config
        self.logger = logger
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None

    def connect(self) -> bool:
        try:
            if self.config.get('connection_string'):
                self.client = MongoClient(self.config['connection_string'])
            else:
                auth_source = f"authSource={self.config['auth_source']}&" if self.config['auth_source'] else ""
                self.config['connection_string'] = (
                    f"mongodb://{quote_plus(self.config['username'])}:"
                    f"{quote_plus(self.config['password'])}@"
                    f"{self.config['host']}:{self.config['port']}/"
                    f"{self.config['db_name']}?{auth_source}"
                    f"directConnection={str(self.config['direct_connection']).lower()}"
                )
                self.client = MongoClient(
                    self.config['connection_string'],
                    connectTimeoutMS=self.config['connect_timeout'],
                    socketTimeoutMS=self.config['socket_timeout'],
                    serverSelectionTimeoutMS=self.config['server_selection_timeout'],
                    appname=self.config['appname']
                )

            self.db = self.client[self.config['db_name']]
            self.collection = self.db[self.config['collection_name']]

            if not self._verify_connection():
                raise ConnectionFailure("Connection verification failed")

            self.logger.log("Connection established", "NETWORK")
            return True

        except Exception as e:
            self.logger.log(f"Connection failed: {str(e)}", "NETWORK", True)
            return False

    def _verify_connection(self) -> bool:
        try:
            self.client.admin.command('ping')
            self.logger.log("Connection verified", "NETWORK")
            return True
        except ConnectionFailure as e:
            self.logger.log(f"Connection verification failed: {str(e)}", "NETWORK", True)
            return False

    def disconnect(self) -> None:
        if self.client and isinstance(self.client, MongoClient):
            self.client.close()
            self.logger.log("Connection closed", "NETWORK")

    def get_collection(self):
        return self.collection

class CreatedAtCleanStrategy(ICleanStrategy):
    def get_query(self, cutoff_date: datetime) -> Dict[str, Any]:
        return {
            "createdAt": {
                "$exists": True,
                "$ne": None,
                "$lt": cutoff_date
            }
        }

# ==================== Main Service ====================
class MongoCleaner:
    def __init__(
        self,
        connector: IDBConnector,
        logger: ILogger,
        clean_strategy: ICleanStrategy,
        retention_days: int = 30
    ):
        self.connector = connector
        self.logger = logger
        self.clean_strategy = clean_strategy
        self.retention_days = retention_days
        self.timezone = timezone.utc

    def calculate_cutoff_date(self) -> datetime:
        return datetime.now(self.timezone) - timedelta(days=self.retention_days)

    def delete_old_documents(self, cutoff_date: datetime) -> int:
        try:
            self.logger.log(f"Cleaning documents older than {cutoff_date.isoformat()}", "CLEANUP")
            collection = self.connector.get_collection()
            result = collection.delete_many(self.clean_strategy.get_query(cutoff_date))
            self.logger.log(f"Deleted {result.deleted_count} documents", "CLEANUP")
            return result.deleted_count
        except PyMongoError as e:
            self.logger.log(f"Deletion failed: {str(e)}", "CLEANUP", True)
            raise

    def compact_collection(self) -> Dict[str, Any]:
        try:
            self.logger.log("Starting collection compaction", "OPTIMIZE")
            collection = self.connector.get_collection()

            # Check if sharded cluster
            if self.connector.client.admin.command('isMaster').get('msg') == 'isdbgrid':
                raise RuntimeError("Cannot compact collection in a sharded cluster")

            result = collection.database.command({
                "compact": collection.name,
                "force": True
            })

            if result.get('ok') == 1:
                self.logger.log("Compaction completed successfully", "OPTIMIZE")
            else:
                self.logger.log(f"Compaction completed with warnings: {result}", "OPTIMIZE")

            return result
        except PyMongoError as e:
            self.logger.log(f"Compaction failed: {str(e)}", "OPTIMIZE", True)
            raise

    def ensure_index(self) -> None:
        collection = self.connector.get_collection()
        if "createdAt_1" not in collection.index_information():
            self.logger.log("Creating index for createdAt field", "INDEX")
            collection.create_index([("createdAt", 1)])

    def get_collection_stats(self) -> Dict[str, Any]:
        try:
            collection = self.connector.get_collection()
            stats = collection.database.command({"collStats": collection.name})

            self.logger.log(f"Statistics of collection: \"{collection.name}\"", "STATS")
            self.logger.log(f"Documents: \t{stats['count']}", "STATS")
            self.logger.log(f"Storage size: \t{stats['storageSize'] / (1024*1024):.2f} MB", "STATS")
            self.logger.log(f"Index size: \t{stats['totalIndexSize'] / (1024*1024):.2f} MB", "STATS")

            return stats
        except PyMongoError as e:
            self.logger.log(f"Failed to get statistics: {str(e)}", "STATS", True)
            raise

    def run(self) -> bool:
        if not self.connector.connect():
            return False

        try:
            cutoff_date = self.calculate_cutoff_date()
            self.delete_old_documents(cutoff_date)
            self.ensure_index()
            self.compact_collection()
            self.get_collection_stats()
            return True
        except Exception as e:
            self.logger.log(f"Cleanup failed: {str(e)}", "SYSTEM", True)
            return False
        finally:
            self.connector.disconnect()

# ==================== Configuration & Startup ====================
def load_config() -> Dict[str, Any]:
    return {
        'connection_string': os.getenv('MONGODB_URI_STRING'),
        'username': os.getenv('MONGODB_DATABASE_ADMIN_USER'),
        'password': os.getenv('MONGODB_USER_ADMIN_PASSWORD'),
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', '27017')),
        'db_name': os.getenv('MONGODB_DB_NAME', 'db'),
        'auth_source': os.getenv('MONGODB_AUTH_SOURCE'),
        'direct_connection': os.getenv('MONGODB_DIRECT_CONNECTION', 'True') == 'True',
        'appname': os.getenv('MONGODB_APP_NAME', 'MongoCleaner'),
        'collection_name': os.getenv('MONGODB_COLLECTION_NAME', 'collection'),
        'connect_timeout': int(os.getenv('MONGODB_CONNECT_TIMEOUT', '5000')),
        'socket_timeout': int(os.getenv('MONGODB_SOCKET_TIMEOUT', '30000')),
        'server_selection_timeout': int(os.getenv('MONGODB_SERVER_SELECTION_TIMEOUT', '20000'))
    }

if __name__ == "__main__":
    config = load_config()
    logger = ConsoleLogger()
    connector = MongoDBConnector(config, logger)
    clean_strategy = CreatedAtCleanStrategy()

    cleaner = MongoCleaner(
        connector=connector,
        logger=logger,
        clean_strategy=clean_strategy,
        retention_days=int(os.getenv('MONGODB_RETENTION_DAYS', '30'))
    )

    cleaner.run()
