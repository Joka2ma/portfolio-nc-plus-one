from pydantic import BaseModel
from datetime import datetime

class EventSummary(BaseModel):
    id: int
    title: str
    starts_at: datetime
    ends_at: datetime
    location:str|None
class EventsResponse(BaseModel):
    
    events:list[EventSummary]
    
    
class EventDetail(BaseModel):
    id: int
    title: str
    description: str | None
    starts_at: datetime
    ends_at: datetime
    location: str | None
    address: str | None
    capacity: int | None
    created_at: datetime
    
class EventResponse(BaseModel):
    event: EventDetail
    

    
    
    
