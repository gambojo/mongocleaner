# mongocleaner

## vars
**Required:**
- MONGODB_DB_NAME - имя базы данных | def: db
- MONGODB_COLLECTION_NAME - имя коллекции | def: collection
- MONGODB_RETENTION_DAYS - сколько дней хранить данные, все что созданно раньше будет удалено | def: 30

**Auth with uri string:**
- MONGODB_URI_STRING - строка подключения

**Auth with parameters:**
- MONGODB_DATABASE_ADMIN_USER - юзер
- MONGODB_USER_ADMIN_PASSWORD - пароль
- MONGODB_HOST - хост | def: localhost
- MONGODB_PORT - порт | def: 27017
- MONGODB_DB_NAME - имя базы | def: db
- MONGODB_AUTH_SOURCE - бд для аутентификации | def: None
- MONGODB_DIRECT_CONNECTION - перенаправление | def: True
- MONGODB_APP_NAME - имя приложения | def: MongoCleaner

**Connect timeout:**
- MONGODB_CONNECT_TIMEOUT - таймаут подключения | def: 5000
- MONGODB_SOCKET_TIMEOUT - таймаут операций | def: 30000
- MONGODB_SERVER_SELECTION_TIMEOUT - таймаут выбора сервера | def: 20000

## Example
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
