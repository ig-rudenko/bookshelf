## Bookshelf

Исходный код сайта с книгами для IT специалистов: [it-bookshelf.ru](https://it-bookshelf.ru).

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)

<div>
  <img height="48" src="/docs/img/docker.svg">
  <img height="48" src="/docs/img/nginx.svg">
  <img height="48" src="/docs/img/vue.svg">
  <img height="48" src="/docs/img/fastapi.svg">
  <img height="48" src="/docs/img/redis.svg">
  <img height="48" src="/docs/img/celery.png">
  <img height="48" src="/docs/img/postgres.svg">
</div>

---

![img.png](docs/img/img.png)

---

### Запуск

Примеры требуемых переменных окружения сервисов находятся в папке `config/env`.

Для каждого сервиса имеется свой файл с переменными окружения.

Применение миграций

```shell
alembic upgrade head;
```

Запуск

```shell
uvicorn main:app
```

### Разработка

Миграции для тестовой базы

```shell
export DATABASE_URL=sqlite+aiosqlite:///test.db;
alembic upgrade head;
```

Тестирование

```shell
python -m unittest discover tests
```