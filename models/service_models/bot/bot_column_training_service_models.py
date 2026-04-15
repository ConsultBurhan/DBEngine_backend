from typing import List, Optional
from pydantic import BaseModel, Field


class BotColumnTrainingList(BaseModel):
    id: str
    schema_name: str
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    column_description: Optional[str] = None
    column_dtype: Optional[str] = None
    synonyms: List[str]
    sample_values: List[str]


class BotColumnTrainingCreate(BaseModel):
    ColumnName: Optional[str] = None
    ColumnType: Optional[str] = None
    ColumnDescription: Optional[str] = None
    SchemaName: Optional[str] = None
    TableName: Optional[str] = None
    Synonyms: Optional[str] = None
    SampleData: Optional[str] = None


class BotColumnTrainingUpdate(BaseModel):
    TrainingId: Optional[str] = None
    ColumnName: Optional[str] = None
    ColumnType: Optional[str] = None
    ColumnDescription: Optional[str] = None
    SchemaName: Optional[str] = None
    TableName: Optional[str] = None
    Synonyms: Optional[str] = None
    SampleData: Optional[str] = None


class BotSpecialTrainingList(BaseModel):
    id: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None


class BotSpecialTrainingCreate(BaseModel):
    text: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
