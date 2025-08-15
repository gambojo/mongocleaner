FROM python:3.11-alpine
WORKDIR /app
COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt && \
    addgroup -g 1001 mongocleaner && \
    adduser -s /bin/sh -h /app -D -u 1001 -G mongocleaner mongocleaner && \
    chown -R mongocleaner:mongocleaner /app
USER mongocleaner
ENTRYPOINT [ "sh", "-c" ]
CMD [ "python mongocleaner.py" ]
