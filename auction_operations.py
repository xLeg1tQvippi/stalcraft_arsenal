from lexicon import lexicon
from colorama import Fore
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.validation import Validator, ValidationError
from typing import Union, Any
from logger import logger

from typing import TYPE_CHECKING
import traceback

import time
import pandas as pd
import tabulate

if TYPE_CHECKING:
    from json_operations import JsonOperations
    from helping_tools import HelpingTools
    from completer_creator import CompleterCreator
    
# from completer_creator import CompleterCreator
# from helping_tools import HelpingTools
# from json_operations import JsonOperations

class AuctionBase:
    def __init__(self, json_operations: "JsonOperations", completer_creator: "CompleterCreator", helping_tools: "HelpingTools"):
        self.jsonOperations = json_operations
        self.helping_tools = helping_tools
        self.completerCreator = completer_creator
        
class Auction:          
    def __init__(self, json_operations, completer_creator, helping_tools):
        self.jsonOperations = json_operations
        self.helping_tools = helping_tools
        self.completerCreator = completer_creator
        self.put_on_auction = PutOnAuction(json_operations=json_operations, completer_creator=completer_creator, helping_tools=helping_tools)
        self.remove_from_auction = RemoveFromAuction(json_operations=json_operations, completer_creator=completer_creator, helping_tools=helping_tools)
        self.show_auction_items = ShowAuctionItems(json_operations=json_operations, completer_creator=completer_creator, helping_tools=helping_tools)
        
    def auction_instructions(self):
        while True:
            self.helping_tools.clear_console()
            print(f"{Fore.YELLOW}{'='*15}{Fore.RESET} Аукцион {Fore.YELLOW}{'='*15}{Fore.RESET}")
            auction_menu: int = self.helping_tools.input_int_handler(f"\nВведите:\n{Fore.CYAN}1{Fore.RESET} - выставить товар на аукцион\n{Fore.CYAN}2{Fore.RESET} - товар куплен (удаление с акциона)\n{Fore.CYAN}3{Fore.RESET} - товар не продан (удаление с аукциона)\n{Fore.CYAN}4{Fore.RESET} - снять лот с аукциона\n{Fore.CYAN}5{Fore.RESET} - текущие лоты на аукционе\n{Fore.YELLOW}0{Fore.RESET} - для выхода\n{Fore.LIGHTCYAN_EX}>>>{Fore.RESET} ", max_value=5, min_value=0)
            if auction_menu == 0:
                return
            
            elif auction_menu == 1:
                # put product on auction
                self.put_on_auction.put_product_on_auction()
            
            elif auction_menu == 2:
                # product has been bought
                self.remove_from_auction.product_has_been_purchased()
            
            elif auction_menu == 3 or auction_menu == 4:
                # product was not sold on auction
                self.remove_from_auction.product_has_not_been_purchased()
            
            elif auction_menu == 5:
                self.show_auction_items.show()
            
class ShowAuctionItems(AuctionBase):
    def __init__(self, json_operations, completer_creator, helping_tools):
        super().__init__(json_operations, completer_creator, helping_tools)
    
    def show(self):
        pd.set_option('display.unicode.east_asian_width', True)
        pd.set_option('display.max_colwidth', None)
        auction_items: dict[str, dict[str, Any]] = self.jsonOperations.read_to_json(lexicon.PATHS['player_data_auction'])
        rows = []
        for product_name, quantities in auction_items.items():
            for quantity, details_list in quantities.items():
                for details in details_list:
                    # Формируем одну строку таблицы
                    row = {
                        "product_name": product_name, # Склеиваем имя и количество
                        "lot": quantity,
                        "buyout_price": details["buyout_price"],
                        "bid_price": details["bid_price"],
                        "price_buy": details['middle_price_buy'] * int(quantity),
                        "due_time": details['product_due_time'],
                        "benefit": details["pre_benefit_calculation"],
                        "deposit_price": details['deposit_price'],
                    }
                    rows.append(row)

        display_df = pd.DataFrame(rows, columns=['product_name', "lot", 'buyout_price', 'price_buy', 'bid_price', 'due_time', "deposit_price", "benefit"])
        display_df["Наименование"] = display_df['product_name']
        display_df['Лот'] = display_df['lot'].map(lambda x: f"{x}шт.")
        display_df['Цена выкупа'] = display_df['buyout_price'].map(lambda x: f"{x:,.0f}р.")
        display_df['Цена ставки'] = display_df['bid_price'].map(lambda x: f"{x:,.0f}р.")
        display_df['Выгода'] = display_df['benefit'].map(lambda x: f"{Fore.GREEN}{x:+,.0f}р.{Fore.RESET}" if x > 0 else f"{Fore.LIGHTRED_EX}{x:,.0f}р.{Fore.RESET}")
        display_df['Срок'] = display_df['due_time']
        display_df['Взнос'] = display_df['deposit_price'].map(lambda x: f"{x:,.0f}р.")
        display_df['Цена покупки'] = display_df['price_buy'].map(lambda x: f"{x:,.0f}р.")
        
        final_cols = ['Наименование', 'Лот', 'Цена выкупа', "Цена покупки", 'Цена ставки', 'Срок', "Взнос", 'Выгода']
        final_df = display_df[final_cols]
        print(tabulate.tabulate(final_df, headers='keys', tablefmt='plain', showindex=False))
        
        input(f"{Fore.MAGENTA}Enter{Fore.RESET} чтобы вернуться в меню.")
        
        
    
class RemoveFromAuction(AuctionBase):
    def __init__(self, json_operations, completer_creator, helping_tools):
        super().__init__(json_operations, completer_creator, helping_tools)
    
    def check_if_product_in_auction(self, product_name: str, auction_items: dict) -> bool:
        try:
            if product_name in auction_items.keys():
                return True
            else:
                return False
            
        except Exception as error:
            logger.error(error)
    
    def get_chosen_lot_data(self, quantity_index: str, buyout_price: int, product_data: dict) -> dict[str, str | int | float]:
        try:
            data_by_quantity_index: list[dict[str, Any]] = product_data[quantity_index]

            if data_by_quantity_index:
                for data in data_by_quantity_index:
                    data: dict[str, str | int | float]
                    if data['buyout_price'] == buyout_price:
                        return data
                                    
        except Exception as error:
            logger.error(error)
            
            
    def choose_lot(self, product_name: str, auction_items: dict[str, dict[str, Any]]):
        def create_choose_lot_list(product_data: dict[str, dict[str, Any]]) -> list[str]:
            try:
                # here we shoould get a product buyout price by quantity index
                #todo: we should keep the similiar data for user to see how many lots he have.
                #todo: but how, if it's impossible to save similiar data as keys to dict.
                #todo: and if to work with list, how to make a completer, if we'd have: [[key, (quantity, data: dict)], [key, (quantity, data: dict)]]
                #todo: the possibility to make a single unique key, and have list of values, but how we will choose values?
                #todo: by index of list?
                #todo: solution: create a unique value and add it to key.
                count = 1
                lot_name_list: list = []
                for quantity, lots_list in product_data.items():
                    lots_data: dict = {}
                    for lot_data in lots_list:
                    # here we get only str quantity object, and then, add it to buyout price.
                        buyout_price: int = lot_data['buyout_price']
                        key: str = f"#{count}| {quantity}шт. - {buyout_price:,}р"
                        lots_data[key] = (quantity, lot_data)
                        lot_name_list.append(key)
                        count += 1
                else:
                    logger.info(f"lot dict before return: {len(lot_name_list)}, lot_name_list: {lot_name_list}")
                    # lot_name_list // structure:
                    """ 
                    [
                        {key=f"{quantity}шт. - {buyout_price:,}р": value=(quantity, lot_data)}
                    ]
                    
                    """
   
                    return lot_name_list, lots_data
            except Exception as error:
                logger.error(error, exc_info=True)
                
        # first we get product data by product_name:
        try:
            product_data: dict[str, Any] = auction_items[product_name]
            # first we get all keys.
            # and creating a list with data.
            # here we reiceve something, kind: '1': product_price: 123, etc
            lot_name_list, lots_data = create_choose_lot_list(product_data=product_data)
            if lot_name_list:
                lot_completer: WordCompleter = WordCompleter(words=lot_name_list, ignore_case=True, match_middle=True, sentence=True)
                print(f"{Fore.YELLOW}0{Fore.RESET} - Выход")
                choose_lot = prompt("Выберите лот: (TAB - Выпадающий список)\n>>> ", completer=lot_completer, complete_while_typing=True)
                if choose_lot == '0':
                    return 0, 0, 0
                
                if choose_lot in lots_data:
                    quantity_index, lot_data = lots_data[choose_lot]
                else:
                    raise KeyError(f"There's no {choose_lot} in {lots_data}.")
                
                print(f"{Fore.GREEN}(>){Fore.RESET} Вы выбрали: {choose_lot}")
            else:
                logger.error("there's not lots with this product name.")
                print(f"{Fore.YELLOW}(>){Fore.RESET} У данного товара нет активных лотов на аукционе.")
                return 0, 0, 0
                
        except Exception as error:
            traceback.print_exc()
            logger.error(error)
        
        else:
            return product_name, quantity_index, lot_data
    
    def remove_product_from_auction(self, product_name: str, quantity_index: str, lot_data: dict[str, str | int | float]) -> bool:
        try:
            player_data_auction: dict[str, dict[str, Any]] = self.jsonOperations.read_to_json(path=lexicon.PATHS['player_data_auction'])
            
            logger.info(f"product quantity before pop: {player_data_auction[product_name][quantity_index]}")
            player_data_auction[product_name][quantity_index].remove(lot_data)
            logger.info('lot has been successfully removed from auction data.')
            
            logger.info(f"product quantity list after pop: {player_data_auction[product_name][quantity_index]}, len: {len(player_data_auction[product_name][quantity_index])}")
            
            if not player_data_auction[product_name][quantity_index]:
                player_data_auction[product_name].pop(quantity_index)
                logger.info(f"quantity index has been removed due to empty data.")
            
            logger.info(f"player_data_auction: {player_data_auction[product_name]}")
            if not player_data_auction[product_name]:
                player_data_auction.pop(product_name)
                
        except Exception as error:
            traceback.print_exc()
            logger.error(error)
            return False
        
        else:
            self.jsonOperations.write_to_json(path=lexicon.PATHS['player_data_auction'], data=player_data_auction)
            return True
    
    def add_product_data_to_player_data_sell(self, product_name: str, quantity_index: str, lot_data: dict[str, str | int | float]) -> dict[str, dict[str, Any]]:
        try:
            player_data_sell: dict[str, dict[str, int | str]] = self.jsonOperations.read_to_json(path=lexicon.PATHS['player_data_sell'])
            
            if product_name not in player_data_sell:
                player_data_sell[product_name] = {
                    # "total_buyout_price": int(lot_data['buyout_price']),
                    "on_sell_price": int(lot_data['buyout_price'] - lot_data['auction_comission']),
                    "total_quantity": int(quantity_index),
                    "middle_price_buy": lot_data['middle_price_buy'],
                    "total_benefit": lot_data['pre_benefit_calculation']
                }
            else:
                # player_data_sell[product_name]["total_buyout_price"] += lot_data['buyout_price']
                player_data_sell[product_name]['on_sell_price'] += (lot_data['buyout_price'] - lot_data['auction_comission'])
                player_data_sell[product_name]['total_quantity'] += int(quantity_index)
                player_data_sell[product_name]['middle_price_buy'] = lot_data['middle_price_buy']
                player_data_sell[product_name]['total_benefit'] += lot_data['pre_benefit_calculation']
        
        except Exception as error:
            logger.error(error)
        
        else:
            self.jsonOperations.write_to_json(path=lexicon.PATHS['player_data_sell'], data=player_data_sell)
            print(f"{Fore.GREEN}(>){Fore.RESET} Данные успешно сохранены в статистику продаж.")
            
    def choose_product_from_auction(self) -> str | int:
        auction_items: dict[str, dict[str, Any]] = self.jsonOperations.read_to_json(path=lexicon.PATHS['player_data_auction']) 
        auction_completer: WordCompleter = self.completerCreator.createCompleter(by='player_data_auction')
        while True:
            print(f"{Fore.YELLOW}0{Fore.RESET} - Выход")
            product_name: str = prompt(f"Выберите товар:\n>>> ", completer=auction_completer)
            if product_name.strip() == '0':
                return 0
            product_in_auction: bool = self.check_if_product_in_auction(product_name=product_name, auction_items=auction_items)      
            if product_in_auction:
                return product_name
            else:
                print(f"{Fore.YELLOW}(>){Fore.RESET} Данного товара нет на аукционе.")
                continue
    
    def return_items_to_vault(self, product_name: str, quantity_index: str, lot_data: dict[str, Any]):
        try:
            # we get all data buy, to check if we already have such product in our vault, for summing data.
            player_data_buy: dict[str, dict[str, int]] = self.jsonOperations.read_to_json(lexicon.PATHS['player_data_buy'])
            middle_price_buy: int = lot_data['middle_price_buy']
            
            product_price = middle_price_buy * int(quantity_index)
            
            if product_name not in player_data_buy:
                player_data_buy[product_name] = {
                    "total_price": product_price,
                    "total_quantity": int(quantity_index),
                }
            else:
                player_data_buy[product_name]["total_price"] += product_price
                player_data_buy[product_name]["total_quantity"] += int(quantity_index)
            
        except Exception as error:
            logger.error(error)
        
        else:
            self.jsonOperations.write_to_json(path=lexicon.PATHS['player_data_buy'], data=player_data_buy)
            print(f"{Fore.GREEN}(>){Fore.RESET} Товар успешно был возвращен на склад.")
    
    def choose_product_and_save_data(self, product_purchased: bool = False, product_not_purchased: bool = False):
        product_name: str | int = self.choose_product_from_auction()
            # so here we making a loop (in another function) for user to choose product
        if product_name == 0:
            return 0
        try:
            while True:
                auction_items: dict[str, dict[str, Any]] = self.completerCreator.get_all_items(by='player_data_auction')
                if auction_items and product_name in auction_items:
                    try:
                        product_name, quantity_index, lot_data = self.choose_lot(product_name=product_name, auction_items=auction_items)
                        if product_name == 0 or quantity_index == 0 or lot_data == 0:
                            return 0
                    except Exception as error:
                        print(f"{Fore.YELLOW}(!){Fore.RESET} Вы допустили ошибку при выборе лота с аукциона. Пожалуйста, повторите попытку.")
                        continue
                    
                    removeStatus: bool = self.remove_product_from_auction(product_name=product_name, quantity_index=quantity_index, lot_data=lot_data)
                    if removeStatus:
                        if product_purchased:
                            self.add_product_data_to_player_data_sell(product_name=product_name, quantity_index=quantity_index, lot_data=lot_data)
                        elif product_not_purchased:
                            self.return_items_to_vault(product_name=product_name, quantity_index=quantity_index, lot_data=lot_data)
                            self.add_product_data_to_player_data_loss(product_name=product_name, quantity_index=quantity_index, lot_data=lot_data)
                    else:
                        logger.error(f"removeStatus: {removeStatus} error unknown, contact developer.")
                else:
                    print(f"{Fore.RED}(!){Fore.RESET} Больше товаров на аукционе нет.")
                    return 0
        except Exception as error:
            logger.error(error)
            print(f"{Fore.YELLOW}(!){Fore.RESET} Произошла ошибка во время выбора лота. Возвращаем обратно...")
            return 0

        finally:
            # for player to see what has been written as logs.
            time.sleep(0.5)
            
    def add_product_data_to_player_data_loss(self, product_name: str, quantity_index: str, lot_data: dict[str, dict[str, Any]]):
        try:
            player_data_loss: dict[str, dict[str, int | str]] = self.jsonOperations.read_to_json(path=lexicon.PATHS['player_data_loss'])
            
            if product_name not in player_data_loss:
                player_data_loss[product_name] = {
                    "total_loss": int(lot_data['deposit_price']),
                    "total_quantity": int(quantity_index)
                }
            else:
                player_data_loss[product_name]["total_loss"] += lot_data['deposit_price']
                player_data_loss[product_name]['total_quantity'] += int(quantity_index)
        
        except Exception as error:
            logger.error(error)
        
        else:
            self.jsonOperations.write_to_json(path=lexicon.PATHS['player_data_loss'], data=player_data_loss)

    def product_has_been_purchased(self):        
        while True:
            quit_status: int = self.choose_product_and_save_data(product_purchased=True)
            if quit_status == 0:
                break
            
    def product_has_not_been_purchased(self):        
        while True:
            quit_status = self.choose_product_and_save_data(product_not_purchased=True)
            if quit_status == 0:
                break
            
class PutOnAuction(AuctionBase):
    def __init__(self, json_operations, completer_creator, helping_tools):
        super().__init__(json_operations, completer_creator, helping_tools)
    
    def product_due_time_prompt_validator(self, text):
        if text not in lexicon.HOURS.keys():
            raise ValidationError(message="Введенного срока нет в списке. Повторите попытку.")
        else:
            return True
    
    def prepare_data_for_save_on_auction(self, product_name: str, bid_price: int, buyout_price: int, middle_price: int, product_due_time: str, auction_comission: int, product_quantity: int, pre_benefit_calculation: int, deposit_price: int):
        try:
            player_data_auction: dict[str, dict[str, int | Any]] = self.jsonOperations.read_to_json(lexicon.PATHS['player_data_auction'])

            if product_name not in player_data_auction:
                player_data_auction[product_name] = {str(product_quantity): [{
                    "bid_price": bid_price,
                    "buyout_price": buyout_price,
                    "middle_price_buy": middle_price,
                    "product_due_time": product_due_time,
                    "auction_comission": auction_comission,
                    "pre_benefit_calculation": pre_benefit_calculation,
                    "deposit_price": deposit_price
                }]}
            else:
                if str(product_quantity) not in player_data_auction[product_name]:
                    player_data_auction[product_name][str(product_quantity)] = []
                    logger.info(f"product quantity not in player data auction product name, set to = [], current: {player_data_auction}")
                
                player_data_auction[product_name][str(product_quantity)].append({
                    "bid_price": bid_price,
                    "buyout_price": buyout_price,
                    "middle_price_buy": middle_price,
                    "product_due_time": product_due_time,
                    "auction_comission": auction_comission,
                    "pre_benefit_calculation": pre_benefit_calculation,
                    "deposit_price": deposit_price
                })
            
            
        except Exception as error:
            logger.error(error)
            
        else:
            return player_data_auction
    
    def sure_to_put_on_auction(self, product_name: str, bid_price: int, buyout_price: int, middle_price: int, product_due_time: str, deposit_price: int, pre_benefit_calculation: int, product_quantity: int, save_times: int, auction_comission: int) -> bool:
        pre_benefit_calculation = f"{f"{Fore.GREEN}{pre_benefit_calculation:,}р.{Fore.RESET}" if pre_benefit_calculation > 0 else f"{Fore.RED}{pre_benefit_calculation:,}р.{Fore.RESET}"}"
        print(f"{"-"*10}\nТовар: {product_name}\nЦена ставки: {bid_price:,}р.\nЦена выкупа: {buyout_price:,}р.\nСрок: {product_due_time}\nЛотов: {save_times} по: {product_quantity}шт.\n{'-'*10}\nВзнос: {deposit_price:,}р.\nВыгода: {pre_benefit_calculation} (по цене покупки за штуку: {middle_price:,}р. | комиссия учтена в цене.)\nКомиссия аукциона: {auction_comission:,}р. (по цене выкупа 5%)\n{"-"*10}")
        sure_to_put_on_auction: int = self.helping_tools.input_int_handler(f"\nВыставляем на аукцион?\n1 - Да\n2 - Нет\n{Fore.LIGHTCYAN_EX}>>>{Fore.RESET} ", min_value=1, max_value=2)
        
        if sure_to_put_on_auction == 1:
            return True
        else:
            return False
    
    def check_if_product_has_this_quantity(self, product_name: str, product_quantity: int) -> bool:
        # checks if the products from vault has given product_quantity. return bool
        if product_name <= 0:
            print(f"{Fore.YELLOW}(!){Fore.RESET} Количество не может быть меньше нуля. Пожалуйста повторите попытку.")
            return False
        player_data_buy: dict[str, dict[str, int]] = self.jsonOperations.read_to_json(lexicon.PATHS['player_data_buy'])
        if player_data_buy[product_name]['total_quantity'] < product_quantity:
            print(f"{Fore.YELLOW}(!){Fore.RESET} Кол-во {product_name} на складе: {player_data_buy[product_name]['total_quantity']}шт.")
            return False
        else:
            return True
        
    def input_product_quantity_on_auction(self, product_name: str) -> Union[int, int]:
        # function that allows us to put on auction n times if products. (according to our player data buy.)
        # so if user wants to put on auction, 3 lots with 10 pieces (so: 10, 10, 10)
        # first we should check if we have this amount on our vault. by: ex: 3*10, (3*10=30) if product_name[quantity] >= 30, we put it on auction
        # else we say that user do not have that amount of product on it's vault.
        # otherwise if user inputs just 10, we save it as lot_pieces = 10, save_times = 1 so we just do one iteration.
        #here we will just save save_times = 3.
        #lot_pieces = 10
        save_times = 1 # default
        while True:
            product_quantity: str = input(f"Разделение: '{Fore.LIGHTMAGENTA_EX}*{Fore.RESET}' | Пример: 10*2: (два лота по 10 штук.)\nВведите кол-во товара\n{Fore.LIGHTCYAN_EX}>>>{Fore.RESET} ")
            if "*" in product_quantity:
                product_quantity_separated: list[str, str] = product_quantity.split('*')
                # we quickly check if both of items are numeric.
                product_quantity: str = product_quantity_separated[0]
                save_times: str = product_quantity_separated[1]
                if product_quantity.isdigit() and save_times.isdigit():
                    # here if both of the product are numeric
                    product_quantity_status: bool = self.check_if_product_has_this_quantity(product_name=product_name, product_quantity=(int(product_quantity)*int(save_times)))
                    if product_quantity_status:
                        # is user has given amount of product on his vault.
                        return int(product_quantity), int(save_times)
                    else:
                        continue
                else:
                    print(f"{Fore.RED}(!){Fore.RESET} Введите числовое значение.")
                    continue
            else:
                if product_quantity.isdigit():
                    product_quantity_status: bool = self.check_if_product_has_this_quantity(product_name=product_name, product_quantity=(int(product_quantity)*save_times))
                else:
                    print(f"{Fore.YELLOW}(!){Fore.RESET} Введите число.")
                    continue
                # if user just inputed a quantity
                if product_quantity_status:
                    return int(product_quantity), save_times
                else:
                    continue
    
    def remove_product_data_from_vault(self, product_name: str, product_quantity: int):
        # here we previously know, that we have right exact amount of product quantity needed for sell. So we just remove it, and save back.
        try:
            player_data_buy: dict[str, dict[str, int]] = self.jsonOperations.read_to_json(path=lexicon.PATHS['player_data_buy'])
            middle_price: int = (player_data_buy[product_name]['total_price'] // player_data_buy[product_name]['total_quantity'])

            if player_data_buy[product_name]['total_quantity'] > product_quantity:
                player_data_buy[product_name]['total_price'] -= (middle_price * product_quantity)
                player_data_buy[product_name]['total_quantity'] -= product_quantity
            
            elif player_data_buy[product_name]['total_quantity'] == product_quantity:
                player_data_buy.pop(product_name)
            
        except Exception as error:
            logger.error(error)
        
        else:
            self.jsonOperations.write_to_json(path=lexicon.PATHS['player_data_buy'], data=player_data_buy)
            print(f"{Fore.GREEN}(>){Fore.RESET} Данные пользователя успешно обновлены.")
    
    def put_product_on_auction(self):
        # first we choose the product according to what we have on our vault
        self.helping_tools.clear_console()
        print(f"{Fore.YELLOW}{'='*15}{Fore.RESET} Выставление товара на аукцион {Fore.YELLOW}{'='*15}{Fore.RESET}")
        player_data_buy: dict[str, dict[str, Any]] = self.completerCreator.get_all_items(by='player_data_buy')
        completer = self.completerCreator.createCompleter(by='player_data_buy')
        while True:
            print(f"\n{Fore.YELLOW}0{Fore.RESET} - Выход")
            product_name: str = prompt(f"Выберите товар: (TAB - Выпадающий список)\n>>> ",completer=completer)
            if product_name == '0':
                return
            if product_name not in player_data_buy:
                print(f"{Fore.YELLOW}(!){Fore.RESET} Данного товара нет на складе.")
                continue
            # so here, we need to ask a person, bid price, buyout price, and for what time he'll put on auction
            if product_name.strip() == "0":
                return
            
            product_data = self.completerCreator.get_all_items(by='player_data_buy')[product_name]
            middle_price: int = product_data['total_price'] // product_data['total_quantity']
            
            # here we output the data about inputed product.
            print(f"{'-'*10}\nТовар: {product_name}\nПокупка: {product_data['total_price']:,}р. - {middle_price:,}р. за штуку.\nКол-во: {product_data['total_quantity']}шт.\n{'-'*10}\n")
            
            bid_price: int = self.helping_tools.input_int_handler(f"Введите стартовую цену (Ставка)\n{Fore.LIGHTCYAN_EX}>>>{Fore.RESET} ",min_value=1)
            if bid_price == 0:
                return
            
            while True:
                buyout_price: int = self.helping_tools.input_int_handler(f"\nВведите цену выкупа\n{Fore.LIGHTCYAN_EX}>>>{Fore.RESET} ", min_value=0)
                if buyout_price == 0:
                    return
                # in case if user wants to set price lower than the bid one~Ё.
                if buyout_price < (bid_price + 1):
                    print(f"{Fore.YELLOW}(>){Fore.RESET} Цена выкупа не может быть меньше ставки. Повторите попытку.")
                    continue
                
                else:
                    break
            
            hour_completer = WordCompleter(words=lexicon.HOURS, ignore_case=True, match_middle=True)
            
            validate_due_time_product = Validator.from_callable(self.product_due_time_prompt_validator)
            product_due_time: str = prompt("Срок: (TAB - Выпадающий список)\n>>> ", completer=hour_completer, validate_while_typing=False, validator=validate_due_time_product)
            
            product_quantity, save_times = self.input_product_quantity_on_auction(product_name=product_name)
            
            deposit_price: int = (bid_price // 100) * lexicon.HOURS[product_due_time]
            auction_comission: int = (buyout_price // 100) * 5 # comission 5% default on auction.
            pre_benefit_calculation: int = ((buyout_price - auction_comission) - (middle_price*product_quantity))
            break
            # now we need to return this data out of cycle
        
        sure_to_put_on_auction: bool = self.sure_to_put_on_auction(product_name=product_name, bid_price=bid_price, buyout_price=buyout_price, middle_price=middle_price, product_due_time=product_due_time, deposit_price=deposit_price, pre_benefit_calculation=pre_benefit_calculation, product_quantity=product_quantity, save_times=save_times, auction_comission=auction_comission)
        if sure_to_put_on_auction:
            for _ in range(save_times):
                prepared_product_data_on_auction = self.prepare_data_for_save_on_auction(product_name=product_name, bid_price=bid_price, buyout_price=buyout_price, middle_price=middle_price, product_due_time=product_due_time, deposit_price=deposit_price, pre_benefit_calculation=pre_benefit_calculation, product_quantity=product_quantity, auction_comission=auction_comission)
                logger.info(f'before save data: {prepared_product_data_on_auction}')
                self.jsonOperations.write_to_json(path=lexicon.PATHS['player_data_auction'], data=prepared_product_data_on_auction)
                self.remove_product_data_from_vault(product_name=product_name, product_quantity=product_quantity)
            else:
                print(f"{Fore.GREEN}(>){Fore.RESET} Данные успешно переданы на аукцион. (x{save_times})")
            return
        else:
            print(f"{Fore.YELLOW}(!){Fore.RESET} Отмена выставки товара на аукцион.")
            return