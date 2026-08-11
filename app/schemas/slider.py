from pydantic import BaseModel, ConfigDict


class SliderCreate(BaseModel):
    display_order: int = 1


class SliderUpdate(BaseModel):
    display_order: int | None = None


class SliderOut(BaseModel):
    id: int
    image: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)