# mongocleaner

## Variables

| Name | Description | Default |
|---|---|---|
| **Required:** |
| MONGODB_DB_NAME | Имя базы данных. | db |
| MONGODB_COLLECTION_NAME | Имя коллекции | collection |
| MONGODB_RETENTION_DAYS | Данные какой давности необходимо сохранить, а все что ранее удалить | 30 |
| **Auth with uri string:** |
| MONGODB_URI_STRING | Строка подключения | - |
| **Auth with parameters:** |
| MONGODB_DATABASE_ADMIN_USER | Пользователь базы данных | - |
| MONGODB_USER_ADMIN_PASSWORD | Пароль пользователя | - |
| MONGODB_HOST | Имя или адрес сервера для подключения | localhost |
| MONGODB_PORT | Порт на котором слушает БД | 27017 |
| MONGODB_AUTH_SOURCE | БД для аутентификации | None |
| MONGODB_DIRECT_CONNECTION | Включить перенаправление | True |
| MONGODB_APP_NAME | Имя клиента (приложения) | MongoCleaner |
| **Connecttion timeouts:** |
| MONGODB_CONNECT_TIMEOUT | Таймаут подключения | 5000 |
| MONGODB_SOCKET_TIMEOUT | Таймаут операций | 30000 |
| MONGODB_SERVER_SELECTION_TIMEOUT | Таймаут выбора сервера | 2000 |

## Examples
**Build**
```bash
docker build -t mongocleaner .
```

**Run with uri string:**
```bash
docker run -it --rm \
    -e MONGODB_URI_STRING="mongodb://username:password@mongodb.example.com:27417/db-name" \
    -e MONGODB_DB_NAME=db-name \
    -e MONGODB_COLLECTION_NAME=collection-name \
    -e MONGODB_RETENTION_DAYS=30 \
    mongocleaner
```

**Run with parameters:**
```bash
docker run -it --rm \
    -e MONGODB_DATABASE_ADMIN_USER=username \
    -e MONGODB_USER_ADMIN_PASSWORD=password \
    -e MONGODB_HOST=mongodb.example.com \
    -e MONGODB_PORT=27417 \
    -e MONGODB_DB_NAME=db-name \
    -e MONGODB_COLLECTION_NAME=collection-name \
    -e MONGODB_RETENTION_DAYS=30 \
    mongocleaner
```
