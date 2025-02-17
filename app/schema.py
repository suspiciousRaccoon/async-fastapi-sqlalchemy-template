from pydantic import BaseModel, ConfigDict


class DefaultModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
