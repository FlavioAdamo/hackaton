from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from services.generate.prompts import extract_content_prompt


class EventSchema(BaseModel):
    scheduled_at: Optional[datetime]
    due_at: Optional[datetime]
    sender_email: Optional[str] = Field(description="email of the sender")
    recipient_email_list: Optional[str] = Field(description="emails of the recipients")
    # recipient_email_list: Optional[List[EmailStr]]
    # sender_email: Optional[EmailStr]
    subject: Optional[str]
    body: Optional[str]
    location: Optional[str]


class DocumentContentExtractionSchema(BaseModel):
    content: str = Field(description=extract_content_prompt)
    event: Optional[EventSchema]
