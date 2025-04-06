# t2_gigabyte_exchange

Воркер для сбора статистики по продаваемым и перемещаемым лотам на бирже Tele2

docker-compose собирает контейнер с воркером, запускает БД Postgres и adminer для доступа к БД на порту 8080

(Переменные окружения с кредами для БД вшиты в docker-compose.yml)

Запуск воркера

```shell
docker compose up -d
```

Остановка воркера

```shell
docker compose down
```
