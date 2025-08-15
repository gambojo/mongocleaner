# mongocleaner

## vars
**Required:**
- MONGODB_DB_NAME - имя базы данных
- MONGODB_COLLECTION_NAME - имя коллекции 
- MONGODB_RETENTION_DAYS - сколько дней хранить данные, все что созданно раньше будет удалено

**Auth with uri string:**
- MONGODB_URI_STRING - строка подключения

**Auth with parameters:**
- MONGODB_DATABASE_ADMIN_USER - юзер
- MONGODB_USER_ADMIN_PASSWORD - пароль
- MONGODB_HOST - хост
- MONGODB_PORT - порт
- MONGODB_DB_NAME - имя базы
- MONGODB_AUTH_SOURCE - бд для аутентификации
- MONGODB_DIRECT_CONNECTION - перенаправление
- MONGODB_APP_NAME - имя приложения

**Connect timeout:**
- MONGODB_CONNECT_TIME - таймаут подключения
- MONGODB_SOCKET_TIMEOUT - таймаут операций
- MONGODB_SERVER_SELECTION_TIMEOUT - таймаут выбора сервера