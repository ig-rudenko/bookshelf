### Запуск
Применение миграций

```shell
export DATABASE_MIGRATION_URL=...  # Без асинхронного драйвера
alembic upgrade head;
```

Переменные окружения:

    DATABASE_URL=   # С асинхронным драйвером

```shell
uvicorn main:app
```

### Разработка

Миграции для тестовой базы

```shell
export DATABASE_MIGRATION_URL=sqlite:///test.db;
alembic upgrade head;
```

Тестирование

```shell
python -m unittest discover tests
```