from pydantic import BaseModel


class FieldModel(BaseModel):
    name: str
    type: str


class GenerateTask(BaseModel):
    rows: int
    fields: list[FieldModel]
    methods: dict
    #db_config: dict | None = None
    #table_name: str | None = None


class DBSaveRequest(BaseModel):
    data: list[dict]
    db_config: dict | None = None
    table_name: str


class AIRequest(BaseModel):
    rows: int
    fields: list[str]


class GeneratorSettings(BaseModel):
    rows: int
    fields: list[dict]