import lmstudio as lms
from faker import Faker

from .utils.parser import parse_csv 
from abc import ABC, abstractmethod

class DataGenerator(ABC):
    def __init__(self, settings):
        self.settings = settings


    @abstractmethod
    def run_generation(self):
        pass


class DataGenerationFaker(DataGenerator):
    def __init__(self, settings):
        super().__init__(settings)
        self.faker = Faker()
        self.column_generators = []


    def field_preparation(self, methods_map: dict):
        for field in self.settings.fields:
            name = field['name']
            method_name = methods_map.get(name)
            generator_func = getattr(self.faker, method_name)
            self.column_generators.append((name, generator_func))


    def run_generation(self) -> list:
        data = []
        for _ in range(self.settings.rows):
            record = {}
            for name, func in self.column_generators:
                record[name] = func()
            data.append(record)
        return data


class DataGeneratorAI(DataGenerator):
    def __init__(self, settings):
        super().__init__(settings)


    def run_generation(self):
        model = lms.llm("google/gemma-3-4b")
        
        params = (
            f"Количество строк: {self.settings.rows}."
            f"Поля: {self.settings.fields}.")
        
        requirements = (
            "Требования к данным:"
            "Сгенерируй синтетический датасет в формате CSV."
            "Выдай только содержимое CSV-файла, начиная с заголовков."
            "Не добавляй никаких пояснений"
            "Если тебе дают требование сгенерировать одну колонку то генерируй одну и БОЛЬШЕ НИЧЕГО"
            "ВСЕГДА добавляй ID если его нет по требованию"
            "Не оборачивай в тройные кавычки, не используй markdown."
            "Разделитель — запятая.")
        
        request = f"{requirements} {params}"
        result = model.respond(request)

        if hasattr(result, 'text') and result.text:
            csv_content = result.text
        elif hasattr(result, 'content') and result.content:
            csv_content = result.content
        else:
            raise ValueError("AI model returned invalid response")
        
        data = parse_csv(csv_content)

        return data
