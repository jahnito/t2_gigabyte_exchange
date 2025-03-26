# t2_gigabyte_exchange

Воркер для сбора статистики по продаваемым и перемещаемым лотам на бирже Tele2

Для запуска БД

```shell
docker compose up -d
```

Сборка контейнера c воркером

```shell
docker build -t worker:0.1 .
```

Для запуска контейнера необходимо передача переменных окружения

```shell
docker run --rm -e PG_USER=postgres -e PG_PASSWD=P@sSw0rd -e PG_HOST=192.168.3.80 -e PG_DBNAME=worker worker:0.1
```
