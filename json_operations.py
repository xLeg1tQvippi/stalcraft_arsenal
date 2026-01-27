from logger import logger
import json
from typing import Any

class JsonOperations:
    def __init__(self):
        pass
    
    def write_to_json(self, path: str, data: dict):
        if data == None:
            data = {}
        try:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as error:
            logger.error('error occured wwhile writing to json.')
        else:
            logger.info('successfully writen to json.')
    
    def read_to_json(self, path: str) -> dict:
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as error:
            logger.error(f'error occured wwhile reading to json. error: {error}')
        else:
            logger.info('successfully writen to json.')
            
    def write_to_file(self, path: str, data: dict | Any):
        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(data)
        except Exception as error:
            logger.error(f'error occured wwhile writing to file ({path}). error: {error}.')
        else:
            logger.info('successfully writen to file.')