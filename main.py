from arsenal_data.arsenal_data_price import arsenal_prices
from player_data_buy import player_data
from player_data_sell import player_data_sell
from player_data_auction import player_data_auction
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import colorama


class Main:
    def __init__(self):
        self.start()
        colorama.init()

    def start(self):
        while True:
            print()
            print(
                "Введите:\n1 - для покупки товаров с аукциона\n2 - выставить\удалить товар на аукцион\n3 - Статистика(Покупка/Продажа), Предварительный рассчет\n4 - рассчет продукта для арсенала\nexit - для выхода"
            )
            choice = input(">>>")
            if choice == "1":
                self.buy_product_instructions()
            elif choice == "2":
                self.sell_product_instructions()
            elif choice == "3":
                self.calculating_instructions()
            elif choice == "4":
                self.count_price_to_arsenal()
            elif choice == "exit":
                break
            else:
                print("Введите 1 или 2")

    # 1 - buy_product_instructions
    # 2 - sell_product_instructions
    # 3 - calculating_instructions я
    # 4 - count_price_to_arsenal

    """ 1.Покупка товаров на аукционе """

    def input_int(self, message):
        while True:
            try:
                return int(input(message))
            except ValueError:
                print("Введите число")
                continue

    def buy_product_instructions(self):
        """Тут находится основная логика последовательности действий."""
        buy_product_status = self.buy_product()
        if buy_product_status == False:
            return
        elif buy_product_status == True:
            returningStatus = self.save_player_data()
            if returningStatus == True:
                print("| Данные о покупке сохранены.")

    def buy_few_products(self, product_name: str, vault_price_amount: list):
        full_product_price: int = int(vault_price_amount[0])
        full_product_quantity: int = int(vault_price_amount[1])

        product_price = full_product_price // full_product_quantity  # Цена за штуку.

        arsenal_price = arsenal_prices.get(product_name)
        total_arsenal = arsenal_price * full_product_quantity
        print(
            f"\nТовар: {product_name}\nКоличество: {full_product_quantity}шт.\nЦена за штуку: {product_price:,}\n"
        )
        would_buy = self.input_int("Покупаем?\n1 - Да\n2 - Нет\n>>>")
        if would_buy == 1:
            return [product_name, product_price, full_product_quantity, total_arsenal]
        if would_buy == 2:
            print("Отменяем покупку...")
            return False
        """ Если товар был куплен в нескольких количествах. """

    def buy_product(self):
        # Просим пользователя ввести название товара
        # И цена товара по которой он скупает
        """Какой предмет купил, за какую цену, в каком количестве"""
        while True:
            total_product_price = 0
            total_quantity = 0
            product_buy_list = {}
            completer = WordCompleter(arsenal_prices.keys(), ignore_case=True)
            product_name = prompt("Введите название товара: ", completer=completer)
            if product_name == "0":
                return False
            if product_name not in arsenal_prices:
                print("Такого товара нет в списке.")
                continue
            while True:
                product_price = input(
                    "Введите \033[1;4mцену товара\033[0m\nВведите \033[4m'/'\033[0m или \033[4m'-'\033[0m после цены для покупки несколько товаров.\n>>>"
                ).replace(" ", "")
                try:
                    if "-" in product_price:
                        product_info = self.buy_few_products(
                            product_name, product_price.split("-")
                        )
                    if "/" in product_price:
                        product_info = self.buy_few_products(
                            product_name, product_price.split("/")
                        )
                    if product_info == False:
                        raise ValueError
                except:
                    if "-" not in product_price or "/" not in product_price:
                        pass
                    else:
                        break
                else:
                    self.add_product_to_player_data(
                        product_name=product_info[0],
                        product_price=(product_info[1] * product_info[2]),
                        product_quantity=product_info[2],
                        total_arsenal=product_info[3],
                    )

                    savingStatus = self.save_player_data()
                    if savingStatus == True:
                        print("| Данные успешно сохранены.")
                        return False
                product_quantity = 0
                product_price = int(product_price)
                if product_price == 0:
                    break
                if product_price < 1000:
                    print("\033[31mОшибка! Минимальная цена товара - 1000р.\033[0m")
                    continue
                product_quantity = self.input_int(
                    "Введите \033[1;4mколичество\033[0m товара: "
                )
                if product_quantity == 0:
                    break
                if product_quantity > 99:
                    print(
                        "\033[31mОшибка! Максимальное вводимое количество товара - 99.\033[0m"
                    )
                    continue
                product_buy_list[str(product_price)] = product_quantity
                total_product_price += product_price * product_quantity
                total_quantity += product_quantity
                print(f"\nОбщая цена: {total_product_price:,}р.")
                [
                    print(f"{int(key):,}р. - x{value}")
                    for key, value in product_buy_list.items()
                ]
                print(f"Общее количество: {total_quantity}\n")
                arsenal_price = arsenal_prices.get(product_name)
                total_arsenal = arsenal_price * product_quantity
                # Сохранение данных о покупке
                self.add_product_to_player_data(
                    product_name,
                    total_product_price,
                    total_quantity,
                    total_arsenal,
                )
                continue
            return True

    def add_product_to_player_data(
        self,
        product_name: str,
        product_price: int,
        product_quantity: int,
        total_arsenal: int,
    ) -> dict:
        """Добавляем данные в статистику игрока о купленных товарах с аукциона."""
        if product_name not in player_data:
            player_data[product_name] = {
                "total_price": product_price,
                "total_quantity": product_quantity,
                "total_arsenal": total_arsenal,
            }
        else:
            player_data[product_name]["total_price"] += product_price
            player_data[product_name]["total_quantity"] += product_quantity
            player_data[product_name]["total_arsenal"] += total_arsenal

    def save_player_data(self) -> bool:
        """Сохраняем данные игрока."""
        with open("player_data_buy.py", "w", encoding="utf-8") as file:
            file.write(f"player_data = {repr(player_data)}")
        return True

    """ 2.Продажа товаров на следующий день """

    def sell_product_instructions(self):
        while True:
            print(
                "Введите:\n1 - для выставки товара на аукцион\n2 - для удаления товара\n0 - для выхода"
            )
            choice = input(">>>")
            if choice == "1":
                status = self.sell_product()
                if status == True:
                    print("Товар выставлен на аукцион.")
            elif choice == "2":
                currentDataAuction = self.remove_product_auction()
                returningStatus = self.save_player_data_auction(player_data_auction)
                if returningStatus == True:
                    print("Сохранено")
            elif choice == "0":
                break

    def sell_product(self):
        while True:
            completer = WordCompleter(player_data.keys(), ignore_case=True)
            product_name = prompt("Введите название товара: ", completer=completer)
            if product_name == "exit":
                break
            while True:
                product_price = input(
                    "Введите \033[4mцену товара\033[0m\nВведите \033[4m'/'\033[0m или \033[4m'-'\033[0m после цены для покупки несколько товаров.\n>>>"
                ).replace(" ", "")
                try:
                    if "-" in product_price:
                        product_info = self.buy_few_products(
                            product_name, product_price.split("-")
                        )
                    if "/" in product_price:
                        product_info = self.buy_few_products(
                            product_name, product_price.split("/")
                        )
                    if product_info == False:
                        raise ValueError
                except:
                    if "-" not in product_price or "/" not in product_price:
                        pass
                    else:
                        break
                else:
                    savingStatus = self.add_product_to_player_data_auction(
                        product_name=product_info[0],
                        product_price=(product_info[1] * product_info[2]),
                        product_quantity=product_info[2],
                    )
                    if savingStatus == True:
                        print("|- Данные успешно сохранены.")
                        return True
                product_price = int(product_price)
                if product_price == 0:
                    break
                if product_price < 1000:
                    print("Минимальная цена товара - 1000р.")
                    continue
                product_quantity = self.input_int("Введите количество товара: ")
                if product_quantity > 99:
                    print("Максимальное вводимое количество товара - 99.")
                    continue
                if product_quantity == 0:
                    break
                status = self.add_product_to_player_data_auction(
                    product_name, (product_price * product_quantity), product_quantity
                )
                if status == True:
                    return True

    def remove_product_auction(self) -> dict:
        """Удаляем товар из статистики игрока о купленных товарах."""
        while True:
            completer = WordCompleter(player_data_auction.keys(), ignore_case=True)
            product_name = prompt("Введите название товара: ", completer=completer)
            print(
                "Количество товара: ",
                player_data_auction[product_name]["total_quantity"],
            )

            if product_name == "exit":
                break
            if product_name not in player_data_auction:
                print("Такого товара нет в списке.")
                continue

            product_quantity = input(
                "Введите количество проданного товара: (0 - чтобы выйти.)\n>>>"
            )
            if product_quantity == "0":
                break
            product_quantity = int(product_quantity)
            middle_price_buy = player_data_auction[product_name]["middle_price_buy"]

            # Цена товара за штуку:
            middle_product_price = (
                player_data_auction[product_name]["total_price"]
                // player_data_auction[product_name]["total_quantity"]
            )

            if player_data_auction[product_name]["total_quantity"] > product_quantity:
                # В случае если количество товара больше чем ввел пользователь.
                player_data_auction[product_name]["total_quantity"] -= product_quantity
                player_data_auction[product_name]["total_price"] = (
                    middle_product_price
                    * player_data_auction[product_name]["total_quantity"]
                )
            elif player_data_auction[product_name]["total_quantity"] < product_quantity:
                print(
                    f"Вы ввели больше чем у вас есть товара. У вас имеется: (x{player_data_auction[product_name]['total_quantity']})"
                )
                continue
            elif (
                player_data_auction[product_name]["total_quantity"] == product_quantity
            ):
                player_data_auction.pop(product_name)
            self.add_product_to_player_data_sell(
                product_name,
                (middle_product_price * product_quantity),
                product_quantity,
                middle_price_buy,
            )
            return player_data_auction

    def add_product_to_player_data_auction(
        self,
        product_name: str,
        product_price: int,
        product_quantity: int,
    ) -> dict:
        """Добавляем данные в статистику игрока о проданных товарах."""
        middle_price_buy = (
            player_data[product_name]["total_price"]
            // player_data[product_name]["total_quantity"]
        )
        if product_name not in player_data_auction:
            player_data_auction[product_name] = {
                "total_price": (product_price // 100) * 95,
                "total_quantity": product_quantity,
                "middle_price_buy": middle_price_buy,
            }
        else:
            player_data_auction[product_name]["total_price"] += (
                product_price // 100
            ) * 95
            player_data_auction[product_name]["total_quantity"] += product_quantity

        status = self.save_player_data_auction(player_data_auction)
        removingStatus = self.remove_product_from_player_data_buy(
            product_name, product_quantity
        )
        print("removingStatus: saved!")
        return status

    def remove_product_from_player_data_buy(
        self, product_name: str, product_quantity: int
    ) -> dict:
        """При выставлении товара на аукцион, удаляем его из статистики покупок."""
        if player_data[product_name]["total_quantity"] > product_quantity:
            player_data[product_name]["total_quantity"] -= product_quantity
            middle_price = (
                player_data[product_name]["total_price"]
                // player_data[product_name]["total_quantity"]
            )
            player_data[product_name]["total_price"] -= middle_price * product_quantity
        elif player_data[product_name]["total_quantity"] < product_quantity:
            print(
                f"Вы ввели больше чем у вас есть товара. У вас имеется: (x{player_data[product_name]['total_quantity']})"
            )
            return False
        elif player_data[product_name]["total_quantity"] == product_quantity:
            player_data.pop(product_name)
        self.save_player_data()
        return True  # Успешно удалено

    def save_player_data_auction(self, player_data_auction: dict) -> bool:
        """Сохраняем данные игрока."""
        with open("player_data_auction.py", "w", encoding="utf-8") as file:
            file.write(f"player_data_auction = {repr(player_data_auction)}")
        print("Данные переданы в файл. (player_data_auction)!")
        return True

    def add_product_to_player_data_sell(
        self, product_name, product_price, product_quantity, middle_price_buy
    ):
        """Добавляем данные в статистику игрока о проданных товарах."""
        if product_name not in player_data_sell:
            player_data_sell[product_name] = {
                "total_price": product_price,
                "total_quantity": product_quantity,
                "middle_price_buy": middle_price_buy,
            }
        else:
            player_data_sell[product_name]["total_price"] += product_price
            player_data_sell[product_name]["total_quantity"] += product_quantity

        self.save_player_data_sell(player_data_sell)

    def save_player_data_sell(self, player_data_sell: dict) -> bool:
        """Сохраняем данные игрока."""
        with open("player_data_sell.py", "w", encoding="utf-8") as file:
            file.write(f"player_data_sell = {repr(player_data_sell)}")
        print("Данные переданы в файл. (player_data_sell)!")

    """ 3. Меню покупки и продажи (Статистика/Рассчет) """

    def calculating_instructions(self):
        while True:
            choice = self.input_int(
                "Введите:\n1 - Статистика продаж/покупок\n2 - предварительный рассчет товара на аукцион\n0 - для выхода\n>>>"
            )
            if choice == 1:
                self.difference()
            elif choice == 2:
                self.preview_calculating()
            elif choice == 0:
                break

    def calculate_priview_prices(self, product_name: str, sell_product_price: int):
        """Рассчитываем выгоду за товар."""
        total_product_price: int = player_data[product_name]["total_price"]
        product_quantity: int = player_data[product_name]["total_quantity"]
        sell_price: int = (
            sell_product_price * product_quantity
        ) / 100  # Продажа товара
        total_sell_price: int = sell_price * 95  # Продажа товара с учетом комиссии
        gain: int = total_sell_price - total_product_price  # Выгода
        return gain

    def preview_calculating(self):
        """Предвраительный рассчет купленных товаров по цене аукциона."""
        print("Введите 'exit' - чтобы выйти.")
        while True:
            completer = WordCompleter(player_data.keys(), ignore_case=True)
            product_name: str = prompt("Введите название товара: ", completer=completer)
            if product_name == "exit":
                break
            if product_name not in player_data:
                print("Такого товара нет в списке.")
                continue
            sell_product_price: int = self.input_int(
                "Введите цену товара за которую хотите продать: "
            )
            gain: int = self.calculate_priview_prices(product_name, sell_product_price)
            print(f"Выгода: {gain:,}р. (С учетом комисии аукциона: 5%)")

    def difference(self):
        print("Разница между покупкой и продажей")
        print(f"\033[33m - Товар на складе -\033[0m")
        for key in player_data.keys():
            print()
            print(f"Товар: {key}")
            print(
                f"Покупка: {player_data[key]['total_price']:,}р. - {player_data[key]['total_price'] // player_data[key]["total_quantity"]:,}р. за штуку."
            )
            print(f"Количество: x{player_data[key]['total_quantity']}")
            try:
                total_arsenal = player_data[key]["total_arsenal"]
                if total_arsenal == 0:
                    raise ValueError
            except ValueError:
                print("Валюта арсенала: У товара нету валюты арсенала.")
            else:
                print(f"Валюта арсенала: {total_arsenal}")
            print()
        print(f"\033[33m- Товар который был уже продан -\033[0m")
        for key in player_data_sell.keys():
            print()
            print(f"Товар: {key} - {player_data_sell[key]['total_quantity']}шт.")
            try:
                middle_price = player_data_sell[key]["middle_price_buy"]
            except:
                print("Выгода: Отсутсвует средняя цена.")
            else:
                print(
                    f"Цена покупки: {middle_price * player_data_sell[key]["total_quantity"]:,}р. ({middle_price:,}р. за штуку.)"
                )
            print(
                f"Продажа: {player_data_sell[key]['total_price']:,} - {player_data_sell[key]['total_price'] // player_data_sell[key]["total_quantity"]:,}р. за штуку."
            )
            print(
                f"Выгода: {player_data_sell[key]['total_price'] - middle_price * player_data_sell[key]['total_quantity']:,}р."
            )
            print(
                f"Окупаемость: {round(player_data_sell[key]['total_price'] / ((middle_price * player_data_sell[key]['total_quantity']) / 100), 1)}%"
            )
        print(
            f"\nВсего денег потрачено: {sum([value["total_price"] for value in player_data.values()]):,}р."
        )
        print(
            f"Всего денег заработано: {sum([value['total_price'] for value in player_data_sell.values()]):,}р.\n"
        )

    """ 4.Рассчет до 10.000 арсенала """

    def count_price_to_arsenal(self):
        arsenal_to_upgrade = 10000
        while True:
            choice = self.input_int(
                "Меню:\n1 - Рассчитать товар до 10.000 за цену\n2 - Рассчитать определенное количество товара для валюты арсена.\n0 - Выйти\n>>>"
            )
            if choice == 1:
                print(
                    f"Данная функция поможет вам рассчитать определенный товар для получения {arsenal_to_upgrade} очков арсенала.\n"
                )
                completer = WordCompleter(arsenal_prices.keys(), ignore_case=True)
                product_name = prompt("Введите название товара: ", completer=completer)
                product_price = self.input_int("Введите цену товара: ")

                product_arsenal_price = arsenal_prices.get(product_name)
                product_quantity = arsenal_to_upgrade / product_arsenal_price
                product_total_price = product_quantity * product_price

                print(
                    f"Для того чтобы получить 10.000 арсенала, вам нужно: {round(product_total_price, 2):,}р.\nКоличество товара: х{round(product_quantity, 2)}"
                )
            if choice == 2:
                completer = WordCompleter(arsenal_prices.keys(), ignore_case=True)
                product_name = prompt("Введите название товара: ", completer=completer)
                product_quantity_to_count = self.input_int(
                    "Введите количество товара для рассчета: "
                )
                print(
                    f"{product_quantity_to_count * arsenal_prices[product_name]} валюты, за x{product_quantity_to_count}шт."
                )
            if choice == 0:
                break


if __name__ == "__main__":
    Main()
