from pydantic import BaseModel, ConfigDict

class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    buildingName: str
    roomNumber: int
    classCode: str | None
    className: str | None
    professor: str | None
    isEmpty: bool