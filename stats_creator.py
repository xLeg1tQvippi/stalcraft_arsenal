import pandas as pd 
from tabulate import SEPARATING_LINE, tabulate
from typing import Any, Union
from colorama import Fore

from json_operations import JsonOperations
from helping_tools import HelpingTools

import logger
from lexicon import lexicon

class StatisticCreator:
    def __init__(self, json_operations, helping_tools):
        self.jsonOperations = json_operations
        self.helping_tools = helping_tools
        self.category_map: dict[str, list[str]] = lexicon.DF_CATEGORIES_MAP
        
    def get_category(self, name):
        for category, items in self.category_map.items():
            if any(item.lower() in name.lower() for item in items):
                return category
        return "Прочее"
    
    def show_statistics(self):
        self.by_player_data_buy()
        self.by_player_data_sell()
        self.by_player_data_loss()
    

    def by_player_data_sell(self):
        player_data_sell: dict[str, dict[str, Any]] = self.jsonOperations.read_to_json(path=lexicon.PATHS['player_data_sell'])
        
        if not player_data_sell:
            print(f"{Fore.RED}Данные о продаже на аукционе - отсутствуют.{Fore.RESET}")
            return

        # 1. Сбор данных в список для создания DataFrame
        rows = []
        for product_name, stats in player_data_sell.items():
            rows.append({
                "category": self.get_category(product_name),
                "product_name": product_name,
                "on_sell_price": stats["on_sell_price"],
                "total_quantity": stats["total_quantity"],
                "middle_price_buy": stats['middle_price_buy'],
                "total_benefit": stats['total_benefit']
            })

        df = pd.DataFrame(rows)

        df['sell_price_per_piece'] = df['on_sell_price'] // df['total_quantity']
        df['total_buy_price'] = df["middle_price_buy"] * df['total_quantity']
        
        total_spend = int(df['total_buy_price'].sum())
        total_earned = int(df['on_sell_price'].sum())
        total_benefit = int(df['total_benefit'].sum())

        df = df.sort_values(["category", "on_sell_price"], ascending=[True, False])

        table_data = []
        headers = [
            "Категория", 
            "Товар", 
            "Цена продажи", 
            "Цена покупки", 
            "Выгода", 
            "Окупаемость", 
            "к-во", 
            "Продажа (шт)", 
            "Покупка (шт)"
        ]
        
        current_category = None

        for _, row in df.iterrows():
            # creating category separating line.
            if current_category is not None and row['category'] != current_category:
                table_data.append(SEPARATING_LINE)

            display_cat = ""
            if row['category'] != current_category:
                current_category = row['category']
                display_cat = f"{Fore.CYAN}{current_category}{Fore.RESET}"

            raw_roi = (row['total_benefit'] / row['total_buy_price'] * 100) + 100 if row['total_buy_price'] > 0 else 0
            
            # allocating color for row of benefits percentage
            if raw_roi >= 100:
                roi_color = Fore.GREEN
            elif 50 <= raw_roi < 100:
                roi_color = Fore.YELLOW
            else:
                roi_color = Fore.RED

            colored_benefit_percentage = f"{roi_color}{round(raw_roi, 1)}%{Fore.RESET}"
            total_benefit = int(row["total_benefit"])
            colored_total_benefit = f"{f"{Fore.GREEN}+{total_benefit:,}{Fore.RESET} р." if total_benefit > 0 else f"{Fore.RED}-{total_benefit:,}{Fore.RESET} р."}"

            table_data.append([
                display_cat,
                row['product_name'],
                f"{int(row['on_sell_price']):,} р.",
                f"{int(row['total_buy_price']):,} р.",
                colored_total_benefit, # colored total benefit
                colored_benefit_percentage, # colored percent benefit
                row['total_quantity'],
                f"{int(row['sell_price_per_piece']):,} р.",
                f"{int(row['middle_price_buy']):,} р."
            ])
            
        print(f"\n{Fore.YELLOW}- Проданный товар -{Fore.RESET}")
        
        col_alignment = ['left'] * 9
        
        # using tablefmt="simple" for SEPARATING_LINE supportance
        print(tabulate(table_data, headers=headers, tablefmt="simple", colalign=col_alignment))

        print(f"\n{Fore.MAGENTA}Всего затрачено:{Fore.RESET}  {total_spend:,} р.")
        print(f"{Fore.MAGENTA}Всего заработано:{Fore.RESET} {total_earned:,} р.")
        print(f"{Fore.GREEN}Чистая выгода:{Fore.RESET}    {total_benefit:,} р.\n")


    def by_player_data_buy(self):
        player_data_buy = self.jsonOperations.read_to_json(path=lexicon.PATHS['player_data_buy'])

        if not player_data_buy:
            print("Данные о покупках отсутствуют.")
            return

        rows = []
        for product_name, stats in player_data_buy.items():
            rows.append({
                "category": self.get_category(product_name),
                "product_name": product_name,
                "total_price": stats["total_price"],
                "quantity": stats["total_quantity"],
                "price_per_piece": stats["total_price"] // stats["total_quantity"]
            })

        # Используем DataFrame только для удобной сортировки
        df = pd.DataFrame(rows).sort_values(["category", "total_price"], ascending=[True, False])

        table_data = []
        headers = ["Категория", "Товар", "Общая цена", "Кол-во", "Цена за шт."]
        current_category = None

        for i, row in df.iterrows():
            # Если категория сменилась — вставляем разделительную линию
            if current_category is not None and row['category'] != current_category:
                table_data.append(SEPARATING_LINE)

            # Если категория новая, добавляем строку с названием категории
            display_cat = ""
            if row['category'] != current_category:
                current_category = row['category']
                display_cat = f"{Fore.CYAN}{current_category}{Fore.RESET}"
                
            # Добавляем данные строки
            table_data.append([
                display_cat,
                row['product_name'],
                f"{row['total_price']:,} р.",
                row['quantity'],
                f"{row['price_per_piece']:,} р."
            ])

        # Подсчет общей суммы
        total_money_spend = df['total_price'].sum()

        print(f"\n{Fore.YELLOW}- Товар на складе -{Fore.RESET}")
        
        # Вывод таблицы. tablefmt="simple" даст чистый вид с подчеркиваниями
        print(tabulate(table_data, headers=headers, tablefmt="simple"))
        
        print(f"\n{Fore.MAGENTA}Всего денег затрачено:{Fore.RESET} {total_money_spend:,} р.\n")
    
    def by_player_data_loss(self):
        player_data_loss: dict[str, dict[str, Any]] = self.jsonOperations.read_to_json(path=lexicon.PATHS['player_data_loss'])
        if not player_data_loss:
            print("Данных о потере при продаже товаров - отсутствует.")
            return
        
        rows = [{
            "total_loss": player_data_loss['total_loss'],
            "total_quantity": player_data_loss['total_quantity']
        }]
        df = pd.DataFrame(rows)
        
        total_loss = df['total_loss'].sum()
        
        df = df.rename({
            "total_loss": "Потеряно",
            "total_quantity": "Кол-во"
        })
        
        df.sort_values(['Потеряно'], ascending=False)
        
        df['Потеряно'] = df['Потеряно'].apply(lambda x: f"{x:,} р.")
        
        df.index.name = f"{Fore.YELLOW}Не проданный товар:{Fore.RESET}"
        
        print(df.to_string(header=False))

if __name__ == "__main__":
    # st = StatisticCreator()
    # st.show_statistics()
    pass