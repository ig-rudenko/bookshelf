from uvicorn import Config, Server

from app.services.logging import setup_logger
from main import app


def run_with_custom_logger(app_, host="0.0.0.0", port=8000):
    """Запуск uvicorn с кастомным логированием"""
    setup_logger()
    config = Config(app_, host=host, port=port, log_config=None)
    server = Server(config)
    server.run()


if __name__ == "__main__":
    run_with_custom_logger(app)
