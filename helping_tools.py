class HelpingTools:
    def __init__(self):
        pass

    def clear_console(self):
        print('\033[H\033[J', end='')
        
    def input_int_handler(self, text: str, max_value: int = None, min_value: int = None) -> int | bool:
        while True:
            try:
                choice = int(input(text))

        
                if max_value != None and min_value != None:
                    if choice < min_value or choice > max_value:
                        print(f"Диапазон выбора должен быть в рамках: {min_value} - {max_value}.")
                        continue
                    else:
                        break
                
                if max_value != None:
                    if choice > max_value or choice <= 0:
                        print(f'Максимально допустимое значение = {max_value}.')
                        continue
                    else:
                        break
                    
                if min_value != None:
                    if choice < min_value:
                        print(f"Минимально допустимое значение = {min_value}.")
                        continue
                    else:
                        break
                    
            except Exception:
                print("Неправильное значение. Пожалуйста повторите попытку.")
                continue
            
            else:
                break
            
        return choice