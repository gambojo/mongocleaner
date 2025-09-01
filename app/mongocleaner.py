#!/usr/bin/env python3

import os
import sys
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime, timedelta, timezone

def log(message: str, prefix: str = "", is_error: bool = False) -> None:
    """Логирование"""
    output = sys.stderr if is_error else sys.stdout
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    print(f"{timestamp} [{prefix}] {message}", file=output)

def create_mongo_connection(config):
    """Подключение к MongoDB"""
    try:
        client = MongoClient(
            host=config['host'],
            port=config['port'],
            document_class=dict,
            username=config['username'],
            password=config['password'],
            authsource=config['auth_source'],
            directconnection=True,
            connectTimeoutMS=config['connect_timeout'],
            socketTimeoutMS=config['socket_timeout'],
            serverSelectionTimeoutMS=config['server_selection_timeout'],
            appname=config['appname']
        )

        # Проверка подключения
        client.admin.command('ping')
        log("Connection established and verified", "NETWORK")

        db = client[config['db_name']]
        collection = db[config['collection_name']]

        # Проверяем, существует ли коллекция в базе данных
        if config['collection_name'] not in db.list_collection_names():
            log(f"Collection {config['collection_name']} is not exists", "NETWORK")
            sys.exit(1)

        return client, collection

    except Exception as e:
        log(f"Connection failed: {str(e)}", "NETWORK", True)
        return None, None

def get_cleanup_query(cutoff_date: datetime) -> dict:
    """Формирование запроса для удаления старых документов"""
    return {
        "createdAt": {
            "$exists": True,
            "$ne": None,
            "$lt": cutoff_date
        }
    }

def compact_collection(client, collection):
    """Сжатие коллекции"""
    try:
        log("Starting collection compaction", "OPTIMIZE")

        # Проверка на шардированный кластер
        if client.admin.command('isMaster').get('msg') == 'isdbgrid':
            raise RuntimeError("Cannot compact collection in a sharded cluster")

        result = collection.database.command({
            "compact": collection.name,
            "force": True
        })

        if result.get('ok') == 1:
            log("Compaction completed successfully", "OPTIMIZE")
        else:
            log(f"Compaction completed with warnings: {result}", "OPTIMIZE")

        return result
    except PyMongoError as e:
        log(f"Compaction failed: {str(e)}", "OPTIMIZE", True)
        raise

def get_collection_stats(collection):
    """Получение статистики коллекции"""
    try:
        stats = collection.database.command({"collStats": collection.name})

        log(f"Statistics of collection: \"{collection.name}\"", "STATS")
        log(f"Documents:  {stats['count']}", "STATS")
        log(f"Storage size:  {stats['storageSize'] / (1024*1024):.2f} MB", "STATS")
        log(f"Index size:  {stats['totalIndexSize'] / (1024*1024):.2f} MB", "STATS")

        return stats
    except PyMongoError as e:
        log(f"Failed to get statistics: {str(e)}", "STATS", True)
        raise

def ensure_index(collection):
    """Создание индекса если его нет"""
    if "createdAt_1" not in collection.index_information():
        log("Creating index for createdAt field", "INDEX")
        collection.create_index([("createdAt", 1)])

def load_config() -> dict:
    """Загрузка конфигурации из переменных окружения"""
    return {
        'username': os.getenv('MONGODB_DATABASE_ADMIN_USER'),
        'password': os.getenv('MONGODB_USER_ADMIN_PASSWORD'),
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', '27017')),
        'db_name': os.getenv('MONGODB_DB_NAME', 'db'),
        'auth_source': os.getenv('MONGODB_AUTH_SOURCE', 'admin'),
        'direct_connection': os.getenv('MONGODB_DIRECT_CONNECTION', 'True') == 'True',
        'appname': os.getenv('MONGODB_APP_NAME', 'MongoCleaner'),
        'collection_name': os.getenv('MONGODB_COLLECTION_NAME', 'collection'),
        'connect_timeout': int(os.getenv('MONGODB_CONNECT_TIMEOUT', '5000')),
        'socket_timeout': int(os.getenv('MONGODB_SOCKET_TIMEOUT', '30000')),
        'server_selection_timeout': int(os.getenv('MONGODB_SERVER_SELECTION_TIMEOUT', '20000'))
    }

if __name__ == "__main__":
    # Загрузка конфигурации
    config = load_config()
    retention_days = int(os.getenv('MONGODB_RETENTION_DAYS', '30'))

    # Подключение к базе
    client, collection = create_mongo_connection(config)

    try:
        # Вычисление времени
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        # Удаление старых документов
        log(f"Cleaning documents older than {cutoff_date.isoformat()}", "CLEANUP")
        result = collection.delete_many(get_cleanup_query(cutoff_date))
        log(f"Deleted {result.deleted_count} documents", "CLEANUP")

        # Создание индекса
        ensure_index(collection)

        # Сжатие коллекции
        compact_collection(client, collection)

        # Получение статистики
        get_collection_stats(collection)

    except Exception as e:
        log(f"Cleanup failed: {str(e)}", "SYSTEM", True)
        sys.exit(1)

    finally:
        # Закрытие подключения
        if client:
            client.close()
            log("Connection closed", "NETWORK")
