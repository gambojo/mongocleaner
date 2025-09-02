# mongocleaner

## Variables
| Name | Description | Default |
|---|---|---|
| MONGODB_DATABASE_ADMIN_USER | Пользователь базы данных | - |
| MONGODB_DATABASE_ADMIN_PASSWORD | Пароль пользователя | - |
| MONGODB_HOSTS | Имена или адреса серверов с портами для подключения | localhost:27417 |
| MONGODB_DB_NAME | Имя базы данных. | db |
| MONGODB_COLLECTION_NAME | Имя коллекции | collection |
| MONGODB_RETENTION_DAYS | Данные какой давности необходимо сохранить, а все что ранее удалить | 30 |
| MONGODB_AUTH_SOURCE | БД для аутентификации | admin |
| MONGODB_DIRECT_CONNECTION | Включить перенаправление | True |
| MONGODB_APP_NAME | Имя клиента (приложения) | MongoCleaner |
| MONGODB_CONNECT_TIMEOUT | Таймаут подключения | 5000 |
| MONGODB_SOCKET_TIMEOUT | Таймаут операций | 30000 |
| MONGODB_SERVER_SELECTION_TIMEOUT | Таймаут выбора сервера | 2000 |
| MONGODB_INDEX_FIELD | Поле по которому будет создан/проверен индекс | createdAt |
| MONGODB_INDEX_ORDER | Направление сортировки | 1 |

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
    -e MONGODB_HOST='mongodb-1.example.com:27417, mongodb-2.example.com:27417, mongodb-3.example.com:27417' \
    -e MONGODB_DB_NAME=db-name \
    -e MONGODB_COLLECTION_NAME=collection-name \
    -e MONGODB_RETENTION_DAYS=30 \
    -e MONGODB_INDEX_FIELD=Idx_field \
    mongocleaner
```
