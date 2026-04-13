"""Stream graph service DTOs for API requests and responses."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class DataPoint(BaseModel):
    """DTO for a single data point in the graph."""
    X: str
    Y: float
    Label: str


class StreamGraphRequest(BaseModel):
    """DTO for stream graph request."""
    User_Query: str
    Bot_Id: int
    Client_Id: int
    Role_Id: int
    Thread_Id: str


class StreamGraphResponse(BaseModel):
    """DTO for stream graph response."""
    Is_Graphable: bool
    Graph_Type: str
    Title: str
    X_Axis_Label: str
    Y_Axis_Label: str
    Data_Points: List[DataPoint]
