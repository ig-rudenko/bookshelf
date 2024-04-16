## Bookshelf

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)

<div>
<img src="https://www.vectorlogo.zone/logos/nginx/nginx-icon.svg" alt="nginx" width="30" height="30"/>
<img src="https://www.vectorlogo.zone/logos/vuejs/vuejs-icon.svg" alt="vue.js" width="30" height="30"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/fastapi/fastapi-original.svg" alt="fastapi" width="30" height="30"/>
<img src="https://www.vectorlogo.zone/logos/postgresql/postgresql-icon.svg" alt="postgresql" width="32" height="32"/>
</div>

---

![img.png](docs/images/img.png)

---

### Запуск

Переменные окружения:

    DATABASE_URL=   # С асинхронным драйвером

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
export DATABASE_URL=sqlite:///test.db;
alembic upgrade head;
```

Тестирование

```shell
python -m unittest discover tests
```