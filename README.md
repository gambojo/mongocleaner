# mongocleaner

## Variables
| Name | Description | Default |
|---|---|---|
| MONGODB_DATABASE_ADMIN_USER | Пользователь базы данных | - |
| MONGODB_DATABASE_ADMIN_PASSWORD | Пароль пользователя | - |
| MONGODB_HOST | Имя или адрес сервера для подключения | localhost |
| MONGODB_PORT | Порт на котором слушает БД | 27017 |
| MONGODB_DB_NAME | Имя базы данных. | db |
| MONGODB_COLLECTION_NAME | Имя коллекции | collection |
| MONGODB_RETENTION_DAYS | Данные какой давности необходимо сохранить, а все что ранее удалить | 30 |
| MONGODB_AUTH_SOURCE | БД для аутентификации | admin |
| MONGODB_DIRECT_CONNECTION | Включить перенаправление | True |
| MONGODB_APP_NAME | Имя клиента (приложения) | MongoCleaner |
| MONGODB_CONNECT_TIMEOUT | Таймаут подключения | 5000 |
| MONGODB_SOCKET_TIMEOUT | Таймаут операций | 30000 |
| MONGODB_SERVER_SELECTION_TIMEOUT | Таймаут выбора сервера | 2000 |

## Examples
**Build**
```bash
docker build -t mongocleaner .
```

**Run:**
```bash
docker run -it --rm \
    -e MONGODB_DATABASE_ADMIN_USER=username \
    -e MONGODB_DATABASE_ADMIN_PASSWORD=password \
    -e MONGODB_HOST=mongodb.example.com \
    -e MONGODB_PORT=27417 \
    -e MONGODB_DB_NAME=db-name \
    -e MONGODB_COLLECTION_NAME=collection-name \
    -e MONGODB_RETENTION_DAYS=30 \
    mongocleaner
```
