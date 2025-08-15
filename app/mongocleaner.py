#!/usr/bin/env python3

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

class MongoCleaner:
    def __init__(self):
        self.connection_string = os.getenv('MONGODB_URI_STRING')
        self.username = os.getenv('MONGODB_DATABASE_ADMIN_USER')
        self.password = os.getenv('MONGODB_USER_ADMIN_PASSWORD')
        self.host = os.getenv('MONGODB_HOST', 'localhost')
        self.port = int(os.getenv('MONGODB_PORT', '27017'))
        self.db_name = os.getenv('MONGODB_DB_NAME', 'db')
        self.auth_source = os.getenv('MONGODB_AUTH_SOURCE', None)
        self.direct_connection = os.getenv('MONGODB_DIRECT_CONNECTION', True)
        self.appname = os.getenv('MONGODB_APP_NAME', 'MongoCleaner')
        self.collection_name = os.getenv('MONGODB_COLLECTION_NAME', 'collection')
        self.retention_days = int(os.getenv('MONGODB_RETENTION_DAYS', '30'))
        self.connect_timeout = int(os.getenv('MONGODB_CONNECT_TIMEOUT', '5000'))
        self.socket_timeout = int(os.getenv('MONGODB_SOCKET_TIMEOUT', '30000'))
        self.server_selection_timeout = int(os.getenv('MONGODB_SERVER_SELECTION_TIMEOUT', '20000'))
        self.timezone = timezone.utc
        self.client = None
        self.db = None
        self.collection = None
        if self.auth_source:
            self.auth_source = f"authSource={self.auth_source}&"


    def get_current_timestamp(self):
        return datetime.now(self.timezone)

    def log(self, message, prefix="", is_error=False):
        output = sys.stderr if is_error else sys.stdout
        print(f"[{self.get_current_timestamp().isoformat()}] {prefix} {message}", file=output)

    def verify_connection(self):
        try:
            self.client.admin.command('ping')
            self.log("Connection verified", "NETWORK")
            return True
        except ConnectionFailure as e:
            self.log(f"Connection verification failed: {str(e)}", "NETWORK", True)
            return False

    def establish_connection(self):
        if not self.connection_string and not self.username:
            self.log("Connection string (MONGO_URI_STRING) is required", "NETWORK", True)
            return False
        try:
            if self.connection_string:
                self.client = MongoClient(self.connection_string)
            else:
                self.connection_string = "mongodb://%s:%s@%s:%s/%s?%sdirectConnection=%s" % (
                    quote_plus(self.username),
                    quote_plus(self.password),
                    self.host,
                    self.port,
                    self.db_name,
                    self.auth_source,
                    str(self.direct_connection).lower())
                self.client = MongoClient(
                    self.connection_string,
                    connectTimeoutMS=self.connect_timeout,
                    socketTimeoutMS=self.socket_timeout,
                    serverSelectionTimeoutMS=self.server_selection_timeout,
                    appname=self.appname
                )
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            if not self.verify_connection():
                raise ConnectionFailure("Connection verification failed")
            self.log("Connection established", "NETWORK")
            return True
        except Exception as e:
            self.log(f"Connection failed: {str(e)}", "NETWORK", True)
            return False

    def calculate_cutoff_date(self):
        return self.get_current_timestamp() - timedelta(days=self.retention_days)

    def delete_old_documents(self, cutoff_date):
        try:
            self.log(f"Cleaning documents older than {cutoff_date.isoformat()}", "CLEANUP")
            result = self.collection.delete_many({
                "createdAt": {
                    "$exists": True,
                    "$ne": None,
                    "$lt": cutoff_date
                }
            })
            self.log(f"Deleted {result.deleted_count} documents", "CLEANUP")
            return result.deleted_count
        except PyMongoError as e:
            self.log(f"Deletion failed: {str(e)}", "CLEANUP", True)
            raise

    def compact_collection(self):
        try:
            self.log("Starting collection compaction", "OPTIMIZE")
            is_mongos = self.client.admin.command('isMaster').get('msg') == 'isdbgrid'
            if is_mongos:
                raise RuntimeError("Cannot compact collection in a sharded cluster")
            result = self.db.command({
                "compact": self.collection_name,
                "force": True
            })
            if result.get('ok') == 1:
                self.log("Compaction completed successfully", "OPTIMIZE")
            else:
                self.log(f"Compaction completed with warnings: {result}", "OPTIMIZE")
            return result
        except PyMongoError as e:
            self.log(f"Compaction failed: {str(e)}", "OPTIMIZE", True)
            raise

    def get_collection_stats(self):
        try:
            stats = self.db.command({"collStats": self.collection_name})
            self.log(f"Statistics of collection: \"{self.collection_name}\"", "STATS")
            self.log(f"Documents: \t{stats['count']}", "STATS")
            self.log(f"Storage size: \t{stats['storageSize'] / (1024*1024):.2f} MB", "STATS")
            self.log(f"Index size: \t{stats['totalIndexSize'] / (1024*1024):.2f} MB", "STATS")
            return stats
        except PyMongoError as e:
            self.log(f"Failed to get statistics: {str(e)}", "STATS", True)
            raise

    def main(self):
        if not self.establish_connection():
            return False
        try:
            cutoff_date = self.calculate_cutoff_date()
            self.delete_old_documents(cutoff_date)
            if "createdAt_1" not in self.collection.index_information():
                self.log("Creating index for createdAt field", "INDEX")
                self.collection.create_index([("createdAt", 1)])            
            self.compact_collection()
            self.get_collection_stats()
            return True
        except Exception as e:
            self.log(f"Cleanup failed: {str(e)}", "SYSTEM", True)
            return False
        finally:
            if self.client and isinstance(self.client, MongoClient):
                self.client.close()
                self.log("Connection closed", "NETWORK")


if __name__ == "__main__":
    cleaner = MongoCleaner()
    cleaner.main()
