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