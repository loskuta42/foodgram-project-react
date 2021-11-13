# Foodgram
Адрес сайта - http://62.84.123.88/recipes/

Сервис «Продуктовый помощник».

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проетке реализовывался backend проекта, а также настройка сервера nginx, frontend был предоставлен в готовом виде.

Проект развернут в докер контейнере 

1. backend - образ бэка проекта
2. frontend - образ фронта проекта
3. postgres - образ базы данных PostgreSQL v 13.02
3. nginx - образ web сервера nginx

## Установка:
Требуется создать файл _.env_ с следующим содержимым:
- ```DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql```
- ```DB_NAME=postgres # имя базы данных```
- ```POSTGRES_USER=postgres # логин для подключения к базе данных```
- ```POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)```
- ```DB_HOST=db # название сервиса (контейнера)```
- ```DB_PORT=5432 # порт для подключения к БД ```
- ```DJANGO_SECRET_KEY = 'p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs'```
- ```DEBUG_VALUE = False```

Далее находясь в корневой папке проекта в терминале прописать(должен быть установлен Docker):
docker-compose up -d --build

И затем следущие команды:
- ```docker-compose exec backend python manage.py makemigrations users --noinput```
- ```docker-compose exec backend python manage.py makemigrations api --noinput```
- ```docker-compose exec backend python manage.py migrate --noinput```
- ```docker-compose exec backend python manage.py createsuperuser```
- ```docker-compose exec backend python manage.py collectstatic --no-input```

