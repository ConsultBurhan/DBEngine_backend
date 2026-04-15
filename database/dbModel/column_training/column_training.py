"""Column training models for database entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class ColumnTraining(_BaseDBModel):
    """Column training entity."""
    TrainingId: int
    ColumnName: Optional[str] = None
    ColumnType: Optional[str] = None
    ColumnDescription: Optional[str] = None
    CreatedDate: Optional[datetime] = None
    CreatedBy: Optional[int] = None
    UpdatedDate: Optional[datetime] = None
    UpdatedBy: Optional[int] = None
    TrainingStatus: Optional[int] = None
    SchemaName: Optional[str] = None
    TableName: Optional[str] = None
    Synonyms: Optional[str] = None
    SampleValues: Optional[str] = None
