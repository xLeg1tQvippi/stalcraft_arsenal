import logging
from pathlib import Path

logging.basicConfig(
    level=logging.ERROR,  # Минимальный уровень для вывода (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s | [%(levelname)s] | %(funcName)s:%(lineno)d | %(message)s',  # Формат: Время [Уровень] Сообщение
    datefmt='%H:%M:%S',  # Формат времени
    handlers=[
        logging.FileHandler(Path(__file__).parent / "logs/main.log", encoding="utf-8"),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)


logger = logging.getLogger("StalcraftApp")