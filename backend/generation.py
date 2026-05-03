import os
import requests
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
        self.lm_studio_host = os.getenv('LM_STUDIO_HOST', 'host.docker.internal')
        self.lm_studio_port = os.getenv('LM_STUDIO_PORT', '2122')
        self.lm_studio_url = f"http://{self.lm_studio_host}:{self.lm_studio_port}/v1/chat/completions"

    def run_generation(self):
        if self.settings.fields and isinstance(self.settings.fields[0], dict):
            field_names = [f['name'] for f in self.settings.fields]
        else:
            field_names = self.settings.fields

        fields_str = ', '.join(field_names)
        expected_columns = ["ID"] + field_names
        cols_count = len(expected_columns)

        header_line = ";".join([f'"{f}"' for f in (["ID"] + field_names)])
        #raw_header = ";".join(["ID"] + field_names)
        example_row = ";".join(['"1"'] + ["Data"] * (cols_count - 1))
        requirements = (
            "ACT AS A DATA GENERATOR. OUTPUT ONLY CLEAN CSV.\n"
            f"STRICTLY FOLLOW THE COLUMN COUNT: {cols_count}\n"
            "RULES:\n"
            "- Use SEMICOLON (;) as the separator.\n"
            "- Wrap EVERY value in double quotes (\").\n"
            "- NO internal commas in names unless specifically asked.\n"
            "- NO conversational filler or backslashes.\n"
        )
        task_description = (
            f"TASK: Generate {self.settings.rows} rows of realistic data.\n"
            f"FIELDS TO GENERATE ({fields_str}).\n"
            "LANGUAGE: RUSSIAN.\n"
            f"OUTPUT FORMAT EXAMPLE:\n{header_line}\n{example_row}"
        )
        prompt = f"{requirements}\n\n{task_description}"
        payload = {
            "messages": [
                {"role": "system", "content": "You are a strict CSV generator. Use SEMICOLON (;) as a separator. "
                "No chat, no markdown."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "seed": -1,
            "max_tokens": 4096
        }
        response_data = requests.post(self.lm_studio_url, json=payload, timeout=2400).json
        csv_content = response_data['choices'][0]['message']['content'].strip()
        data = parse_csv(text=csv_content, expected_columns=expected_columns)
        yield from data