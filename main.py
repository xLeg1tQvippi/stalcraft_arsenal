from colorama import Fore, Style
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from pathlib import Path
import json
from logger import logger
from typing import Any, Union
from lexicon import lexicon
import time
import traceback

from auction_operations import Auction
from helping_tools import HelpingTools
from json_operations import JsonOperations
from completer_creator import CompleterCreator
from stats_creator import StatisticCreator

class ArsenalMenu:
    def __init__(self):
        self.jsonOperations = JsonOperations()
        self.helping_tools = HelpingTools()
        self.completer_creator = CompleterCreator()
        self.buyProduct = BuyProduct()
        self.sellProduct = Auction(json_operations=self.jsonOperations, completer_creator=self.completer_creator, helping_tools=self.helping_tools)
        self.productCaluclation = ProductCalculation()
        self.stats_creator = StatisticCreator(json_operations=self.jsonOperations, helping_tools=self.helping_tools)
    
    def start(self):
        while True:
            print()
            print(
                f"Введите:\n{Fore.CYAN}1{Fore.RESET} - Покупка товаров\n{Fore.CYAN}2{Fore.RESET} - Аукцион\n{Fore.CYAN}3{Fore.RESET} - Статистика (Покупка/Продажа), Предварительный рассчет\n{Fore.CYAN}4{Fore.RESET} - рассчет продукта для арсенала\nexit - для выхода"
            )
            choice = input(">>>")
            if choice == "1":
                self.buyProduct.buy_product_instructions()
            elif choice == "2":
                self.sellProduct.auction_instructions()
            elif choice == "3":
                pass
                self.stats_creator.show_statistics()
            elif choice == "4":
                pass
                # self.count_price_to_arsenal()
            elif choice == "exit":
                break
            else:
                print("Введите правильное значение")
                continue
            
class BuyProduct:
    def __init__(self):
        self.helping_tools = HelpingTools()
        self.completerCreator = CompleterCreator()
        self.jsonOperations = JsonOperations()
    
    def buy_product_instructions(self):
        """Тут находится основная логика последовательности действий."""
        buy_product_status = self.buy_product()
        if buy_product_status == False:
            return
        elif buy_product_status == True:
            returningStatus = self.save_player_data()
            if returningStatus == True:
                print("| Данные о покупке сохранены.")
    
    def choose_product(self) -> str | int:
        try:
            while True:
                print(f"{Fore.LIGHTYELLOW_EX}0{Fore.RESET} - Выход")
                product_name = prompt(f"Введите название товара: (TAB - Для выпадающего списка)\n>>> ", completer=self.completerCreator.createCompleter(by='main_filenames'))
                all_items: list[str] = self.completerCreator.get_all_items(by='main_filenames')
                # we check if product name is not zero
                if product_name.strip() != '0':
                    if product_name in all_items:
                        return product_name
                    else:
                        # todo make a possibility to add a new product in list to auction items.
                        print(f"{Fore.CYAN}(>){Fore.RESET} Вы ввели товар которого не существует в базе.")
                        continue
                else:
                    return 0
        except Exception as error:
            logger.error(error)
    
    def get_product_price(self, product_name: str) -> Union[int, int]:
        # main menu for inputing prices for a product.
        try:
            product_price = input(
                f"\n{Fore.YELLOW}Опции покупки{Fore.RESET}:\nРазделение: '{Fore.LIGHTMAGENTA_EX}-{Fore.RESET}' | Пример: 1200-2: 600р за 2.\nРазделение: '{Fore.LIGHTMAGENTA_EX}*{Fore.RESET}' | Пример: 600*2: 1200р (два лота по 600)\n{Fore.YELLOW}0{Fore.RESET} - Завершить покупки\n\nВведите {Fore.LIGHTYELLOW_EX}цену{Fore.RESET} товара: {Fore.LIGHTBLUE_EX}{product_name}{Fore.RESET}\n>>> "
            ).replace(" ", "")
            
            if product_price.strip() == '0':
                return 0, 0
            
            # so, now we check either if "*" or "-" in price.
            if "-" in product_price:
                product_price, product_quantity = self.buy_product_substraction(separated_product_price=product_price.split('-'))
            
            elif "*" in product_price:
                product_price, product_quantity = self.buy_product_multiplication(separated_product_price=product_price.split('*'))
        
            else:
                product_price, product_quantity = self.buy_product_default(product_name=product_name, product_price=product_price)

        except Exception as error:
            logger.error(error)
            
        else:
            return product_price, product_quantity
    
    def prepare_data_for_save(self, product_name: str, product_price: int, product_quantity: int) -> dict[str, dict[str, int]]:
        try:
            logger.info(f"recieved: price: {product_price}, quantity: {product_quantity}")
            prepared_data_for_save: dict = {}
            
            # we get all data buy, to check if we already have such product in our vault, for summing data.
            player_data_buy: dict[str, dict[str, int]] = self.jsonOperations.read_to_json(lexicon.PATHS['player_data_buy'])
            
            product_price = product_price * product_quantity
            
            if product_name not in player_data_buy:
                player_data_buy[product_name] = {
                    "total_price": product_price,
                    "total_quantity": product_quantity,
                }
            else:
                player_data_buy[product_name]["total_price"] += product_price
                player_data_buy[product_name]["total_quantity"] += product_quantity
            
        except Exception as error:
            logger.error(error)
        
        else:
            return player_data_buy
    
    def sure_to_buy(self, product_name: str, product_prices_list: list[str, int]) -> bool:
        print(f"{'-'*(7+len(product_name))}\nТовар: {product_name}")
        for product_prices in product_prices_list:
            print(f"Цена: {product_prices["product_price"]:,}р. - {product_prices["product_quantity"]}шт.")
        else:
            print('-'*10)
        
        buy_choose: int = self.helping_tools.input_int_handler(f'Покупаем?\n{Fore.CYAN}1{Fore.RESET} - Да\n{Fore.CYAN}2{Fore.RESET} - Нет\n{Fore.LIGHTCYAN_EX}>>>{Fore.RESET} ', min_value=1, max_value=2)
        
        if buy_choose == 1:
            return True
        else:
            return False
        
    def buy_product_default(self, product_name: str, product_price: str):
        # if user do not inputed any of signs in product_price.
        product_quantity: int = self.helping_tools.input_int_handler(f"{Fore.YELLOW}0{Fore.RESET} - Выход\nВведите количество: (Товар: {product_name})\n{Fore.LIGHTCYAN_EX}>>>{Fore.RESET} ")
        
        return int(product_price), int(product_quantity)
    
    def buy_product_multiplication(self, separated_product_price: list[str, str]) -> Union[int, int]:
        # when sign '*' in product price. (600*2)
        product_quantity: int = int(separated_product_price[1])
        product_price: int = int(separated_product_price[0])
        
        return product_price, product_quantity
    
    def buy_product_substraction(self, separated_product_price: list[str, str]) -> Union[int, int]:
        # when sign '-' in product price. (1200-2)
        product_price: int = int(separated_product_price[0])
        product_quantity: int = int(separated_product_price[1])
        
        price_per_piece: int = product_price // product_quantity
        
        return price_per_piece, product_quantity
    
    def show_current_buy_cart(self, product_name: str, product_prices_list: list[dict[str, int]]):
        print(f"-----{Fore.LIGHTMAGENTA_EX} Корзина {Fore.RESET}-----")
        print(f"Товар: {product_name}")
        for product_prices in product_prices_list:
            print(f"Цена: {product_prices["product_price"]:,}р. - {product_prices["product_quantity"]}шт.")
        else:
            print(f"-------{Fore.LIGHTMAGENTA_EX} -~- {Fore.RESET}-------")
    
    def buy_product(self):
        self.helping_tools.clear_console()
        print(f"{f'{Fore.YELLOW}='*15}{Fore.RESET} Покупка товаров {f'{Fore.YELLOW}='*15}{Fore.RESET}")
        # Просим пользователя ввести название товара
        # И цена товара по которой он скупает
        """Какой предмет купил, за какую цену, в каком количестве"""
        while True:
            product_prices_list: list = []
            product_name: str | int = self.choose_product()
            
            if product_name == 0:
                # zero code is equal to quit.
                break
            while True:
                price_quantity_data: dict = {"product_price": 0, "product_quantity": 0}
                product_price, product_quantity = self.get_product_price(product_name=product_name)

                if product_price == 0 or product_quantity == 0:
                    break
                
                price_quantity_data["product_price"] = product_price
                price_quantity_data["product_quantity"] = product_quantity
                
                product_prices_list.append(price_quantity_data)
                self.show_current_buy_cart(product_name=product_name, product_prices_list=product_prices_list)
                
            sure_to_buy_choose: bool = self.sure_to_buy(product_name=product_name, product_prices_list=product_prices_list)
            if sure_to_buy_choose:
                for product_prices in product_prices_list:
                    product_price: int = product_prices['product_price']
                    product_quantity: int = product_prices['product_quantity']
                    data_for_save: dict[str, dict[str, int]] = self.prepare_data_for_save(product_name=product_name, product_price=product_price, product_quantity=product_quantity)
                    self.jsonOperations.write_to_json(path=lexicon.PATHS['player_data_buy'], data=data_for_save)
                print(f"{Fore.GREEN}(>){Fore.RESET} Данные о покупки успешно сохранены.")
                self.helping_tools.clear_console()
    
class ProductCalculation:
    def __init__(self):
        pass

if __name__ == "__main__":
    try:
        a = ArsenalMenu()
        a.start()
    except Exception as error:
        traceback.print_exc()
        logger.error(error, exc_info=True)
        
        input("Enter to continue...")