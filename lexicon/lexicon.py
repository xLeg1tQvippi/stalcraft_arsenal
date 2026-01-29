from pathlib import Path
from colorama import Fore
from json_operations import JsonOperations
import json

PATHS: dict[str, str] = {
    "artefacts": fr"{Path(__file__).parent.parent}\auction_items\artefacts.json",
    "artefacts_with_rarities": fr"{Path(__file__).parent.parent}\auction_items\artefacts_with_rarities.json",
    "auction_items": fr"{Path(__file__).parent.parent}\auction_items\auction_items.json",
    "premium_items": fr"{Path(__file__).parent.parent}\auction_items\premium_items.json",
    "player_data_auction": fr"{Path(__file__).parent.parent}\player_data\player_data_auction.json",
    "player_data_buy": fr"{Path(__file__).parent.parent}\player_data\player_data_buy.json",
    "player_data_sell": fr"{Path(__file__).parent.parent}\player_data\player_data_sell.json",
    "player_data_loss": fr"{Path(__file__).parent.parent}\player_data\player_data_loss.json",
    "logs": fr"{Path(__file__).parent.parent}\logs\main.log",
    "main_filenames": ["auction_items", "premium_items", "artefacts_with_rarities"]
}

HOURS: dict[str, int] = {
    "6ч": 1, # 1% comission
    "12ч": 2, # 2% comission
    "24ч": 3, # 3% comission
    "48ч": 5 # 5% comission
}

COLORS = {
    "ORANGE": '\033[38;2;255;128;0m',
    "DEFAULT": '\033[38;2;192;192;192m',
    "LIGHT1": '\033[38;2;180;210;185m',
    "LIGHT2": '\033[38;2;140;210;155m',
    "LIGHT3": '\033[38;2;100;210;125m',
    "LIGHT4": '\033[38;2;50;215;85m',
    "LIGHT5": '\033[38;2;0;235;55m',
    "LIGHT6": '\033[38;2;155;255;0m',
    "GOLDEN": '\033[38;2;255;240;0m'
}

COLORED_ARTEFACT_RARITY_LIST: list[str] = [f"{Fore.WHITE}Обычный", f"{Fore.LIGHTGREEN_EX}Необычный", f"{Fore.LIGHTBLUE_EX}Особый", f"{Fore.MAGENTA}Редкий", f"{Fore.LIGHTRED_EX}Исключительный", f"{Fore.LIGHTYELLOW_EX}Легендарный"]
NON_COLORED_ARTEFACT_RARITY_LIST: list[str] = ['Обычный', "Необычный", 'Особый', "Редкий", 'Исключительный', "Легендарный"]

def get_df_categories_map() -> dict[str, list[str]]:
    DF_CATEGORIES_MAP = {}
    paths_to_json_categories: list = [str(f.absolute()) for f in (Path(__file__).parent.parent / "product_categories").iterdir()]
    for path_to_json in paths_to_json_categories:
        with open(path_to_json, 'r', encoding='utf-8') as file:
            jsonCategory: dict[str, list] = json.load(file)
        for category_name, category_data in jsonCategory.items():
            DF_CATEGORIES_MAP[category_name] = category_data

    else:
        return DF_CATEGORIES_MAP
            
            
            
DF_CATEGORIES_MAP = {
    "Броня": ["Комбинезон", "Бронекостюм", "Экзоброня", "Костюм"],
    "Оружие": ["HK PSG1"],
    "Обвесы": ["Sig Sauer", "Прицел"], 
    "Артефакты": [
        "Опал",
        "Кристалл Изнанки",
        "Нервяк",
        "Висмут",
        "Харя",
        "Ключик",
        "Рубик",
        "Силки",
        "Сетчатка",
        "Смольник",
        "Изюм",
        "Обруч",
        "Темная калина",
        "Жабры",
        "Бубльгум",
        "Черная дыра",
        "Канифоль",
        "Роза Изнанки",
        "Яйцо",
        "Личинка",
        "Полено",
        "Смалец",
        "Гребешок",
        "Пиявка",
        "Корка",
        "Красный кристалл",
        "Иней",
        "Глаз бури",
        "Каблук",
        "Жар-птица",
        "Морозец",
        "Радиатор",
        "Куриный бог",
        "Солнце",
        "Ветка Калины",
        "Фаренгейт",
        "Вихрь",
        "Волчьи слезы",
        "Хрусталь",
        "Огонек",
        "Сало",
        "Прима",
        "Протоцибуля",
        "Сердце",
        "Проклятая роза",
        "Янтарник",
        "Ягодка",
        "Вехотка",
        "Креветка",
        "Плод",
        "Роза",
        "Браслет",
        "Белая роза",
        "Темный кристалл",
        "Остов",
        "Жильник",
        "Криоген",
        "Гантель",
        "Цибуля",
        "Болотный гнилец",
        "Золотистая Прима",
        "Липкий репях",
        "Змеиный глаз",
        "Флегма",
        "Стальной Ежик",
        "Репях",
        "Ершик",
        "Кислотный кристалл",
        "Ряска",
        "Улитка",
        "Многогранник",
        "Жвачка",
        "Чернильница",
        "Скорлупа",
        "Ежик",
        "Кисель",
        "Трещотка",
        "Лампочка Ильича",
        "Ледяной ежик",
        "Осколок",
        "Призрачный кристалл",
        "Комета",
        "Спираль",
        "Гелий",
        "Трансформатор",
        "Дезинтегратор",
        "Атом",
        "Гиря",
        "Призма",
        "Батарейка",
        "Зеркало"
    ],
    }

