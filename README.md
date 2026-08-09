## Bookshelf

Исходный код сайта с книгами для IT специалистов: [it-bookshelf.ru](https://it-bookshelf.ru).

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)

![](https://go-skill-icons.vercel.app/api/icons?i=typescript,vite,vuejs,primevue,tailwindcss&perline=10)

![](https://skills.syvixor.com/api/icons?i=python,astraluv,uvicorn,fastapi,pydantic,sqlalchemy,celery&perline=12&radius=40)

![](https://go-skill-icons.vercel.app/api/icons?i=nginx,docker,redis,postgresql,s3&perline=10)

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