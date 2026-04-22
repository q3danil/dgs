import abc
import csv
from pathlib import Path


def get_downloads_folder() -> Path:
    home = Path.home()
    downloads = home / "Downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads


EXPORT_DIR = get_downloads_folder()


class SaveData(abc.ABC):
    def __init__(self, data):
        if not data:
           raise ValueError("Data cannot be empty")
        if not isinstance(data, list):
            raise ValueError("Data must be a list of dictionaries")
        self.data = data    


    @abc.abstractmethod
    def save(self, destination):
        pass


class SaveDataToCSV(SaveData):
    def save(self, file_name):
        if not file_name.endswith(".csv"):
            file_name += ".csv"
        
        full_path = EXPORT_DIR / file_name
        full_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(self.data[0].keys())
        with open(full_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.data)
        return str(full_path)
