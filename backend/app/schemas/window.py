from pydantic import BaseModel, Field

class WindowUpdate(BaseModel):
    width: float = Field(gt=0)
