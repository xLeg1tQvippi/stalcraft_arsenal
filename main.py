from arsenal_data.arsenal_data_price import arsenal_prices
from player_data_buy import player_data
from player_data_sell import player_data_sell
from player_data_auction import player_data_auction
from player_data_loss import player_data_loss
from wordCompleterDicts import hours
import pandas as pd
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import os
import colorama


class Main:
    def __init__(self):
        colorama.init()
        self.start()

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
    # 3 - calculating_instructions
    # 4 - count_price_to_arsenal

    def input_int(self, text: str):
        while True:
            try:
                text = int(input(text))
            except:
                print("введите число")
                continue
            else:
                return text

    """ 1.Покупка товаров на аукционе """

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
            return [
                product_name,
                product_price,
                full_product_quantity,
                full_product_price,
            ]
        if would_buy == 2:
            print("Отменяем покупку...")
            return False
        """ Если товар был куплен в нескольких количествах. """

    def show_product_buy_list(self, product_buy_list: dict, total_price: int):
        total_quantity = 0
        print(f"\nОбщая цена: {total_price:,}р.")
        for key, value in product_buy_list.items():
            total_quantity += value
            print(f"{int(key):,}р. - x{value}")
        print(f"Общее количество: {total_quantity}шт.\n")

    def buy_product(self):
        # Просим пользователя ввести название товара
        # И цена товара по которой он скупает
        """Какой предмет купил, за какую цену, в каком количестве"""
        while True:
            total_product_price = 0
            full_product_price_buy_few = 0
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
                    f"Введите \033[1;4mцену товара\033[0m - покупаем: {product_name} (Доступно разделение: 54000-5 (То есть, 5 товаров за 54000. (Целый лот)))\n>>>"
                ).replace(" ", "")
                if product_price == "0":
                    break
                buy_few_products_status = [False, False]
                denyingPayment = False
                buy_few_products_bool_status = False
                try:
                    if "-" in product_price:
                        product_info = self.buy_few_products(
                            product_name, product_price.split("-")
                        )
                        if product_info != False:
                            buy_few_products_status[0] = True
                    else:
                        buy_few_products_status[0] = False
                    if "/" in product_price:
                        product_info = self.buy_few_products(
                            product_name, product_price.split("/")
                        )
                        if product_info != False:
                            buy_few_products_status[1] = True
                    else:
                        buy_few_products_status[1] = False
                    if product_info == False:
                        denyingPayment = True
                        continue
                    # Проверка статусов.

                    if (
                        buy_few_products_status[0] == False
                        and buy_few_products_status[1] == False
                    ):
                        buy_few_products_bool_status = False
                        raise ValueError

                except:
                    if buy_few_products_bool_status == False:
                        pass
                else:
                    self.add_product_to_player_data(
                        product_name=product_info[0],
                        product_price=(product_info[1] * product_info[2]),
                        product_quantity=product_info[2],
                    )
                    product_buy_list[str(product_info[1])] = product_info[2]
                    total_product_price += product_info[3]
                    self.show_product_buy_list(
                        product_buy_list,
                        total_product_price,
                    )
                    continue
                product_quantity = 0
                product_price = int(product_price)
                if product_price == 0:
                    break
                if product_price < 200:
                    print("\033[31mОшибка! Минимальная цена товара - 200.\033[0m")
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
                if str(product_price) in product_buy_list.keys():
                    product_buy_list[str(product_price)] += product_quantity
                else:
                    product_buy_list[str(product_price)] = product_quantity
                total_product_price += product_price * product_quantity
                self.add_product_to_player_data(
                    product_name, product_price * product_quantity, product_quantity
                )

                self.show_product_buy_list(
                    product_buy_list, total_price=total_product_price
                )
                continue
            return True

    def add_product_to_player_data(
        self,
        product_name: str,
        product_price: int,
        product_quantity: int,
    ) -> dict:
        """Добавляем данные в статистику игрока о купленных товарах с аукциона."""
        try:
            total_arsenal = arsenal_prices[product_name] * product_quantity
        except:
            total_arsenal = 0
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
                "Введите:\n1 - для выставки товара на аукцион\n2 - товар куплен (удаление с акциона)\n3 - товар не продан (удаление с аукциона)\n0 - для выхода"
            )
            choice = input(">>>")
            if choice == "1":
                status = self.sell_product()
                if status == True:
                    print("Товар выставлен на аукцион.")
            elif choice == "2":
                while True:
                    closingStatus = self.remove_product_auction_success()
                    if closingStatus == 0:
                        break
                    returningStatus = self.save_player_data_auction(player_data_auction)
                    if returningStatus == True:
                        print("Сохранено")
            elif choice == "3":
                closingStatus = self.remove_product_auction_failure()
                if closingStatus == 0:
                    break
                pass
            elif choice == "0":
                break

    def check_product_price(self, text: str):
        while True:
            try:
                product_price = int(input(text))
            except Exception as error:
                continue
            else:
                if product_price == 0:
                    return 0
                if product_price < 1000:
                    print("Минимальная цена товара - 1000р.")
                    continue
                else:
                    return product_price

    def check_if_miltuply_sell_product(self, text: str):
        try:
            if "*" in text:
                separate = text.split("*")
                separate = [int(obj) for obj in separate]
                return [separate, True]
            else:
                raise ValueError
        except:
            return [text, False]

    def input_check_product_quantity(self, text: str):
        while True:
            try:
                product_quantity = input(text)
                status_data = self.check_if_miltuply_sell_product(product_quantity)
                if status_data[1] == True:
                    return [status_data[0], True]
                if status_data[1] == False:
                    product_quantity = int(product_quantity)
            except Exception as error:
                print("Введите число", error)
                continue
            else:
                if product_quantity == 0:
                    return 0
                if product_quantity > 500:
                    print("Максимальное вводимое количество товара - 500.")
                    continue
                else:
                    return [product_quantity, False]

    def check_product_quantity(self, product_name: str, product_quantity: int):
        if product_name not in player_data.keys():
            print("Товар отсутствует")
        else:
            if player_data[product_name]["total_quantity"] < product_quantity:
                return False
            else:
                return True

    def show_product_data(self, product_name: str):
        if product_name in player_data.keys():
            print(f"\nТовар: {product_name}")
            print(
                f"Покупка: {player_data[product_name]['total_price']:,}р. - {player_data[product_name]['total_price'] // player_data[product_name]['total_quantity']:,}р. за штуку."
            )
            print(f"Количество: x{player_data[product_name]['total_quantity']}")
        print()

    def sell_product(self):
        while True:
            completer_hours = WordCompleter(hours.keys(), ignore_case=True)
            completer_item_name = WordCompleter(player_data.keys(), ignore_case=True)
            product_name = prompt(
                "Введите название товара: ", completer=completer_item_name
            )
            if product_name == "0":
                break
            self.show_product_data(product_name)
            while True:
                starting_price = self.input_int(
                    "\033[4;1mСтартовая\033[0m цена товара: "
                )
                if starting_price == 0:
                    break
                product_price = self.check_product_price(
                    "Цена \033[4;1mвыкупа:\033[0m "
                )
                if product_price == 0:
                    break

                while True:
                    product_living_hours = prompt("Срок: ", completer=completer_hours)
                    if product_living_hours not in hours.keys():
                        print("Введено неверное время.")
                        continue
                    else:
                        break
                while True:
                    product_quantity = self.input_check_product_quantity(
                        "Введите количество товара '10*4':"
                    )
                    if type(product_quantity[0]) == list:
                        product_quantity_check = (
                            product_quantity[0][0] * product_quantity[0][1]
                        )
                        status = self.check_product_quantity(
                            product_name, product_quantity=product_quantity_check
                        )
                    else:
                        status = self.check_product_quantity(
                            product_name, product_quantity=product_quantity[0]
                        )
                    if status == False:
                        print(
                            f"Количество товара на складе: {player_data[product_name]['total_quantity']}"
                        )
                        continue
                    if status == True:
                        break
                if product_quantity == 0:
                    break
                if product_quantity[1] == True:
                    count = 0
                    for i in range(product_quantity[0][1]):
                        if count == product_quantity[0][1]:
                            print("breaking!")
                            break
                        status = self.add_product_to_player_data_auction(
                            product_name=product_name,
                            starting_price=starting_price,
                            product_price=product_price,
                            product_quantity=product_quantity[0][0],
                            product_hours=hours[product_living_hours],
                        )
                        count += 1
                if product_quantity[1] == False:
                    status = self.add_product_to_player_data_auction(
                        product_name=product_name,
                        starting_price=starting_price,
                        product_price=product_price,
                        product_quantity=product_quantity[0],
                        product_hours=hours[product_living_hours],
                    )
                if status == True:
                    return True

    def select_product_and_data(self) -> dict:
        items_completer = WordCompleter(player_data_auction.keys(), ignore_case=True)
        selected_item = prompt("Выберите товар: ", completer=items_completer)
        if selected_item == 0:
            return 0

        selected_data = None  # Полные данные варианта
        selected_quantity_key = None  # Сюда сохраним ключ (например, "2")

        # Проверяем, есть ли товар в словаре и содержит ли он варианты
        if selected_item in player_data_auction and isinstance(
            player_data_auction[selected_item], dict
        ):
            options = {}

            for quantity, entries in player_data_auction[selected_item].items():
                if isinstance(entries, list):  # Если есть вложенные списки с ценами
                    for entry in entries:
                        key = f"{quantity} - {entry['product_price']}"  # "2 - 325000"
                        options[key] = (quantity, entry)  # Сохраняем (ключ, данные)

            if options:
                # **ШАГ 2:** Выбираем конкретный вариант
                quantity_completer = WordCompleter(options.keys(), ignore_case=True)
                selected_option = prompt(
                    "Выберите вариант: ", completer=quantity_completer
                )

                # **ШАГ 3:** Получаем полный объект и его ключ
                selected_quantity_key, selected_data = options[selected_option]

                print("\nВы выбрали:", selected_option)
                return [selected_item, selected_quantity_key, selected_data]
            else:
                print("Для данного товара нет вариаций с ценами.")
        else:
            print("Ошибка: товар не найден или не содержит вариантов.")

    def remove_product_auction_failure(self):
        """Удаляет товар из статистики аукциона и возвращает количество обратно в player_data."""
        while True:
            # Получаем [название товара, ключ количества, данные]
            data = self.select_product_and_data()
            if data == None:
                return 0
            selected_product = data[0]  # "лямбда"
            selected_quantity_key = data[1]  # "2"
            selected_data = data[2]  # Данные конкретного варианта

            if not selected_data:
                print("Ошибка: данные не найдены.")
                continue

            product_variants = player_data_auction.get(selected_product, {}).get(
                selected_quantity_key, []
            )

            # Находим индекс выбранного варианта
            try:
                selected_index = product_variants.index(selected_data)
            except ValueError:
                print("Ошибка: вариант товара не найден.")
                continue

            # Извлекаем удаляемый вариант
            removed_data = product_variants.pop(selected_index)
            if not product_variants:
                del player_data_auction[selected_product][selected_quantity_key]

            # Если после удаления не осталось вариантов — удаляем товар полностью
            if not player_data_auction[selected_product]:
                del player_data_auction[selected_product]

            self.save_player_data_auction(player_data_auction)
            # Возвращаем товар обратно в player_data
            self.return_product_to_player_inventory(
                selected_product, selected_quantity_key, removed_data
            )

    def create_returning_data(
        self, product_name: str, selected_quantity_key: str, removed_data: dict
    ):
        total_price = removed_data["middle_price_buy"] * int(selected_quantity_key)
        product_arsenal = arsenal_prices.get(product_name)
        total_arsenal = product_arsenal * int(selected_quantity_key)
        data = {
            "total_price": total_price,
            "total_quantity": int(selected_quantity_key),
            "total_arsenal": total_arsenal,
        }
        return data

    def save_player_data_loss(self, product_name: str, quantity: str, lossity: int):
        if product_name in player_data_loss.keys():
            player_data_loss[product_name]["loss"] += lossity
            player_data_loss[product_name]["total_quantity"] += int(quantity)

        if product_name not in player_data_loss.keys():
            player_data_loss[product_name] = {
                "loss": lossity,
                "total_quantity": int(quantity),
            }

        with open("player_data_loss.py", "w", encoding="utf-8") as file:
            file.write(f"player_data_loss = {repr(player_data_loss)}")
            print("player_data_loss saved!")

    def calculate_player_data_loss(
        self, product_name: str, selected_quantity_key: str, removed_data: dict
    ):
        hours_loss = {6: 1, 12: 2, 24: 3, 48: 5}
        lossity = (removed_data["starting_price"] / 100) * hours_loss[
            removed_data["product_hours"]
        ]
        self.save_player_data_loss(product_name, selected_quantity_key, lossity)

    def create_add_return_product_data(
        self, product_name: str, selected_quantity_key: str, removed_data: dict
    ):
        total_price = removed_data["middle_price_buy"] * int(selected_quantity_key)
        product_arsenal = arsenal_prices.get(product_name)
        total_arsenal = product_arsenal * int(selected_quantity_key)
        player_data[product_name]["total_price"] += total_price
        player_data[product_name]["total_quantity"] += int(selected_quantity_key)
        player_data[product_name]["total_arsenal"] += total_arsenal
        return True

    def return_product_to_player_inventory(
        self, product_name: str, selected_quantity_key: str, removed_data: dict
    ):
        print(
            f"product_name: {product_name}\nselected quantity: {selected_quantity_key}, removed_data: {removed_data}"
        )
        """Требуется получить данные о изначальной цене продукта за 1 шт: complete"""
        if product_name in player_data.keys():
            returnDataStatus = self.create_add_return_product_data(
                product_name, selected_quantity_key, removed_data
            )
            print("product_name in player_data!")
        if product_name not in player_data.keys():
            player_data[product_name] = self.create_returning_data(
                product_name, selected_quantity_key, removed_data
            )
            print("product_not_in_player_data!")
        print("Данные успешно возвращены в список покупок.")
        self.calculate_player_data_loss(
            product_name, selected_quantity_key, removed_data
        )
        print("Возвращаем предмет на склад...")
        self.save_player_data()

    def remove_product_auction_success(self) -> dict:
        """Удаляем товар из статистики игрока о купленных товарах."""
        while True:
            data = self.select_product_and_data()
            if data == None:
                return 0
            selected_product = data[0]  # "лямбда"
            selected_quantity_key = data[1]  # "2"
            selected_data = data[2]  # Данные конкретного варианта

            if not selected_data:
                print("Ошибка: данные не найдены.")
                continue

            product_quantity = int(selected_quantity_key)  # "2" → 2
            middle_price_buy = selected_data["middle_price_buy"]
            middle_product_price = (
                selected_data["product_price"] // product_quantity
            )  # Цена за одну штуку

            # Список всех вариантов товара с таким количеством
            product_variants = player_data_auction[selected_product][
                selected_quantity_key
            ]

            # Находим индекс выбранного варианта
            try:
                selected_index = product_variants.index(selected_data)
            except ValueError:
                print("Ошибка: вариант товара не найден.")
                continue

            # Проверяем, если у товара есть другие вариации, обновляем данные
            if len(product_variants) > 1:
                product_variants.pop(selected_index)  # Удаляем конкретный вариант
            else:
                # Если это был единственный вариант, удаляем весь ключ количества
                del player_data_auction[selected_product][selected_quantity_key]

            # Если после удаления не осталось вариантов — удаляем товар полностью
            if not player_data_auction[selected_product]:
                del player_data_auction[selected_product]

            # Добавляем в статистику продажи
            self.add_product_to_player_data_sell(
                selected_product,
                (middle_product_price * product_quantity),
                product_quantity,
                middle_price_buy,
            )

            return player_data_auction  # Возвращаем обновленный словарь

    def create_data_add_auction(self, product_quantity: int, data: dict) -> dict:
        creating_data = {f"{product_quantity}": data}
        return creating_data

    def add_product_to_player_data_auction(
        self,
        product_name: str,
        starting_price: int,
        product_price: int,
        product_quantity: int,
        product_hours: int,
    ) -> bool:
        """Добавляем данные в статистику игрока о проданных товарах."""
        middle_price_buy = (
            player_data[product_name]["total_price"]
            // player_data[product_name]["total_quantity"]
        )
        if product_name not in player_data_auction:
            player_data_auction[product_name] = self.create_data_add_auction(
                product_quantity,
                [
                    {
                        "starting_price": starting_price,
                        "product_price": product_price,
                        "product_hours": product_hours,
                        "middle_price_buy": middle_price_buy,
                    }
                ],
            )
        else:
            if f"{product_quantity}" not in player_data_auction[product_name]:
                player_data_auction[product_name][f"{product_quantity}"] = []

            player_data_auction[product_name][f"{product_quantity}"].append(
                {
                    "starting_price": starting_price,
                    "product_price": product_price,
                    "product_hours": product_hours,
                    "middle_price_buy": middle_price_buy,
                }
            )
        status = self.save_player_data_auction(player_data_auction)
        removingStatus = self.remove_product_from_player_data_buy(
            product_name, product_quantity
        )
        print("removingStatus: saved!")
        return status

    def remove_product_from_player_data_buy(
        self, product_name: str, product_quantity: int
    ) -> dict:
        print("remove product!", product_quantity)
        """При выставлении товара на аукцион, удаляем его из статистики покупок."""
        middle_price = (
            player_data[product_name]["total_price"]
            // player_data[product_name]["total_quantity"]
        )
        if player_data[product_name]["total_quantity"] > product_quantity:
            player_data[product_name]["total_quantity"] -= product_quantity
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
        product_price_after_tax = (product_price / 100) * 95  # Учитываем комиссию 5%

        if product_name not in player_data_sell:
            player_data_sell[product_name] = {
                "total_price": product_price_after_tax,
                "total_quantity": product_quantity,
                "middle_price_buy": middle_price_buy,
            }
        else:
            player_data_sell[product_name]["total_price"] += product_price_after_tax
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
                "Введите:\n1 - Статистика продаж/покупок\n2 - Поиск купленного товара\n3 - предварительный рассчет товара на аукцион\n0 - для выхода\n>>>"
            )
            if choice == 1:
                self.difference()
            if choice == 2:
                self.search_bought_product()
            elif choice == 3:
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
        print(f"name: {product_name}, total_product_price: {total_product_price}, product_quantity: {product_quantity}, sell_price: {sell_price}, total_sell_price: {total_sell_price}")
        gain: int = total_sell_price - total_product_price  # Выгода
        print('gain:', gain)
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

    def create_dataFrame_player_data(self):
        df = pd.DataFrame.from_dict(player_data, orient="index")
        df = df.rename(
            columns={
                "total_price": "общая_цена",
                "total_quantity": "количество",
                "total_arsenal": "репутация",
            }
        )
        df["цена_шт"] = df["общая_цена"] // df["количество"]
        total_price_summed = df["общая_цена"].sum()
        total_reputation = df["репутация"].sum()
        df["цена_шт"] = df["цена_шт"].apply(lambda x: f"{round(x, 2):,}р.")
        df.index.name = "\033[4m\033[0m\033[33m - Товар на складе -\033[0m"
        df = df.sort_values(by=["общая_цена"], ascending=[False])
        df = [df, total_price_summed, total_reputation]
        print(df[0])
        print(
            f"\033[4mВсего денег затрачено\033[0m: {df[1]:,}р.\n\033[4mВсего репутации арсенала:\033[0m {df[2]:,}\n"
        )

    def create_dataFrame_player_data_loss(self):
        df = pd.DataFrame.from_dict(player_data_loss, orient="index")
        df = df.rename(columns={"loss": "потеряно", "total_quantity": "количество"})
        df.index.name = "\033[33mНе купленный товар\033[0m"
        total_lost = df["потеряно"].sum()
        df["потеряно"] = df["потеряно"].apply(lambda x: f"{int(x):,}р.")
        print(df)
        print(f"Всего потеряно: {total_lost:,}р.")

    def create_dataFrame_player_data_sell(self):
        df = pd.DataFrame.from_dict(player_data_sell, orient="index")
        df = df.rename(
            columns={
                "total_price": "цена_продажи",
                "total_quantity": "кол-во",
                "middle_price_buy": "цена_покупки_шт",
            }
        )
        df.index.name = "\033[4m\033[0m\033\033[33m - Проданный товар -\033[0m"
        total_price_sell = df["цена_продажи"].sum()
        df = df.sort_values(by=["цена_продажи"], ascending=[False])

        df["цена_продажи_шт"] = df["цена_продажи"] // df["кол-во"]
        df["цена_покупки"] = df["цена_покупки_шт"] * df["кол-во"]
        total_price_buy = df["цена_покупки"].sum()
        df["выгода"] = (df["цена_продажи_шт"] - df["цена_покупки_шт"]) * df["кол-во"]
        total_prodit = df["выгода"].sum()
        df["окупаемость"] = df.apply(
            lambda row: f"{round((row['цена_продажи'] / (row['цена_покупки_шт'] * row['кол-во'])) * 100, 1)}%",
            axis=1,
        )

        df["выгода"] = df["выгода"].apply(lambda x: f"{int(x):,}р.")
        df["цена_продажи"] = df["цена_продажи"].apply(lambda x: f"{int(x):,}р.")
        df["цена_покупки"] = df["цена_покупки"].apply(lambda x: f"{int(x):,}р.")
        df["цена_продажи_шт"] = df["цена_продажи_шт"].apply(lambda x: f"{int(x):,}р.")
        df["цена_покупки_шт"] = df["цена_покупки_шт"].apply(lambda x: f"{int(x):,}р.")
        df = df.reindex(
            columns=[
                "цена_продажи",
                "цена_покупки",
                "выгода",
                "окупаемость",
                "кол-во",
                "цена_продажи_шт",
                "цена_покупки_шт",
            ]
        )
        print(df.to_string())
        print(
            f"\nВсего денег потрачено: {total_price_buy:,}р.\nВсего денег заработано: {round(total_price_sell):,}р.\nВыгода за все товары: {total_prodit:,}р.\n"
        )

    def difference(self):
        print("Разница между покупкой и продажей")
        self.create_dataFrame_player_data()
        self.create_dataFrame_player_data_sell()
        self.create_dataFrame_player_data_loss()

    def search_bought_product(self):
        while True:
            completer = WordCompleter(player_data.keys(), ignore_case=True)
            search_product = prompt(
                "Введите товар который желаете найти: ", completer=completer
            )
            if search_product == "0":
                break
            if search_product in player_data.keys():
                print(f"\nТовар: {search_product}")
                print(
                    f"Покупка: {player_data[search_product]['total_price']:,}р. - {player_data[search_product]['total_price'] // player_data[search_product]['total_quantity']:,}р. за штуку."
                )
                print(f"Количество: x{player_data[search_product]['total_quantity']}")

                total_arsenal = player_data[search_product].get("total_arsenal", 0)
                if total_arsenal == 0:
                    print("Валюта арсенала: У товара нету валюты арсенала.")
                else:
                    print(f"Валюта арсенала: {total_arsenal}")
                print()

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
    # os.system("mode con: cols=120 lines=30")
    Main()
