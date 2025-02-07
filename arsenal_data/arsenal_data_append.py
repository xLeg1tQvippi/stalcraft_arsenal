from arsenal_data_price import arsenal_prices
from pathlib import Path


def arsenal_data_append():
    while True:
        barter = input("Enter the name of the barter item: ")
        if barter == "exit":
            break
        else:
            price = input("Enter the price of the barter item: ")
            arsenal_prices[barter] = int(price)
    return arsenal_prices


def save_data(new_price_list: dict):
    script_dir = Path(__file__).parent
    file_path = script_dir / "arsenal_data_price.py"
    with file_path.open("w", encoding="utf-8") as file:
        file.write(f"arsenal_prices = {repr(new_price_list)}")
    return True


new_prices = arsenal_data_append()
print(new_prices)
saving = save_data(new_prices)
if saving == True:
    print("Успешно сохранено!")
