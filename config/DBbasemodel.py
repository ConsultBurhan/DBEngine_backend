from pydantic import BaseModel, ConfigDict, Field


class _BaseDBModel(BaseModel):
    """Shared pydantic config for DB models."""
    model_config = ConfigDict(from_attributes=True)

