![yamdb_workflow](https://github.com/Nizzerato/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

# yamdb_final

## Описание проекта

- Проект YamDB позволяет пользователям оставлять отзывы, комментарии и оценки к различным произведениям самых разных жанров, будь то фильмы, книги, музыка или что бы то ни было. "yamdb_final" - это финальная ступень YamDB, в которой был разработан workflow, автоматически запускающий тесты, проводящий контейнеризацию и запускающий проект на боевой сервер, с последующим уведомлением разработчика в Telegram при успешном запуске.

# Доступность проекта

Проект доступен по адресу: 51.250.101.1
Документация доступна по адресу: 51.250.101.1/redoc/

# Как скачать, установить и запустить проект локально:

Локально проект будет вам доступен по адресу: http://127.0.0.1
Документация к проекту будет локально доступна по адресу: http://127.0.0.1/redoc/

Склонируйте репозиторий в рабочее пространство командой:

```
git clone https://github.com/Nizzerato/yamdb_final.git
```

## Запуск проекта:

- Соберите и запустите проект командой:

```
docker-compose up -d --build
```

- Создайте миграции:

```
docker-compose exec web python manage.py migrate
```

- Соберите статику проекта:

```
docker-compose exec web python manage.py collectstatic --no-input
```

Глобальные настройки проекта находятся в файле `api_yamdb/settings.py`

## Создание суперпользователя

- Выполните команду:

```
docker-compose exec -ti container_name python manage.py createsuperuser
```

## Наполнение базы данных тестовыми данными

- Выполните команду:

```
docker-compose exec -ti container_name python manage.py loaddata fixtures.json
```

## Пример наполнения .env-файла:

```
SECRET_KEY=(Этот ключ находится в настройках проекта)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

# Tech
**Python**, **Django**, **Rest Framework**, **Simple-JWT**, **NGINX**, **Docker**, **Gunicorn**

# Автор
[Nizzerato](https://github.com/Nizzerato)
