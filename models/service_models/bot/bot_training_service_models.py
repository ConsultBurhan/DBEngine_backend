"""Pydantic models for bot training service DTOs."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BotsTrainingListing(BaseModel):
    """Bot training listing model."""
    Id: int
    Type: Optional[int] = None
    Subid: Optional[int] = None
    Trainingtext: Optional[str] = None
    Embeddingdb: Optional[str] = None
    Embeddingdetails: Optional[str] = None
    Botid: Optional[int] = None
    Status: Optional[str] = None
    Issqlquery: Optional[bool] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None


class ViewMetadata(BaseModel):
    """View metadata model."""
    Schema_Name: str
    View_Name: str
    Description: str
    Synonyms: List[str]
    RelationShip: str


class ColumnMetadata(BaseModel):
    """Column metadata model."""
    ColumnId: int
    Synonyms: List[str]
    Description: str
    RelationShip: str


class CreateBotDatabaseTraining(BaseModel):
    """Create bot database training model."""
    View_Metadata: ViewMetadata
    Columns_Metadata: List[ColumnMetadata]
    ConnectionId: int
    BotId: str
    RoleId: str


class CreateBotGenralTraining(BaseModel):
    """Create bot general training model."""
    BotId: int
    TrainingType: int
    TraingingText: str
    QuestionText: str
    Source: int
    BotResponseRatingId: Optional[int] = None


class UpdateBotTraining(BaseModel):
    """Update bot training model."""
    Trainingtext: str
    Botid: int
    Status: str
