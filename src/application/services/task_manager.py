from abc import ABC
from collections.abc import Callable


class TaskManager(ABC):

    class TaskNotFound(Exception): ...

    async def register_task(self, name: str, task: Callable):
        """
        Регистрирует задачу с указанным именем и функцией.
        Args:
            name: Имя задачи.
            task: Функция задачи.
        """

    async def run_task(self, name: str, *args, **kwargs) -> str:
        """
        Запускает задачу с заданным именем и возвращает идентификатор задачи.
        Args:
            name: Имя задачи.
            *args: Аргументы для задачи.
            **kwargs: Ключевые аргументы для задачи.
        Returns:
            str: Идентификатор задачи.
        Raises:
            TaskNotFound: если задача с указанным именем не найдена.
        """
