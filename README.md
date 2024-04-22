## Bookshelf

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)

<div>
<img src="https://www.vectorlogo.zone/logos/nginx/nginx-icon.svg" alt="nginx" width="30" height="30"/>
<img src="https://www.vectorlogo.zone/logos/vuejs/vuejs-icon.svg" alt="vue.js" width="30" height="30"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/fastapi/fastapi-original.svg" alt="fastapi" width="30" height="30"/>
<img src="https://www.vectorlogo.zone/logos/redis/redis-icon.svg" alt="redis" width="30" height="30"/>
<img src="https://camo.githubusercontent.com/564a444c6463b93f21b09c004b48389d9db89df23affa4abfd34ac2d43956388/68747470733a2f2f6861766f6c612e757a2f75706c6f6164732f6c6f676f732f39302f73623475306771762e706e67" alt="celery" width="30" height="30"/>
<img src="https://www.vectorlogo.zone/logos/postgresql/postgresql-icon.svg" alt="postgresql" width="32" height="32"/>
</div>

---

![img.png](docs/images/img.png)

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