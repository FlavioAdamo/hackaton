from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class EventSchema(BaseModel):
    scheduled_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    recipient_email_list: Optional[List[EmailStr]] = None
    sender_email: Optional[EmailStr] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    location: Optional[str] = None


class GeminiInputSchema(BaseModel):
    content: str = "First, identify what type of document this is (e.g. image, CV, invoice, etc.) and provide a brief 1-2 sentence summary of its overall content. Then, analyze the document and carefully extract all the information, presenting it in a human readable format without structured markup. Please ensure all content is written in English, translating from other languages if necessary."
    event: Optional[EventSchema] = None
