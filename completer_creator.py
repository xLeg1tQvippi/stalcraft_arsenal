from helping_tools import HelpingTools
from json_operations import JsonOperations
from lexicon import lexicon
from logger import logger
from prompt_toolkit.completion import WordCompleter

class CompleterCreator:
    def __init__(self):
        self.helping_tools = HelpingTools()
        self.jsonOperations = JsonOperations()

    def get_all_items(self, by: str):
        # main_filenames, player_data_buy
        auction_file_name_list: list[str] | str = lexicon.PATHS[by]
        all_items: list = []
        try:
            if type(auction_file_name_list) == list:
                for file_name in auction_file_name_list:
                    full_file_path: Path = lexicon.PATHS[file_name]
                    items: dict[str, list[str]] = self.jsonOperations.read_to_json(path=full_file_path)
                    all_items.extend(items['items'])
            else:
                all_items: dict[str, dict[str, int]] = self.jsonOperations.read_to_json(path=auction_file_name_list)
                
        
        except Exception as error:
            logger.error(error, exc_info=True)
            
        else:
            return all_items
        
    def createCompleter(self, by: str):        
        try:
            completer = WordCompleter(words=self.get_all_items(by), match_middle=True, ignore_case=True)
        except Exception as error:
            logger.error(error)
            
        else:
            logger.info("word completer has been successfully prepared.")
            return completer
