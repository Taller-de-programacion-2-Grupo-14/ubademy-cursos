from typing import List, Optional
from pydantic import BaseModel, Field, validator
from exceptions.CourseException import InvalidSubscriptionType

SUBSCRIPTION_TYPES = ["basico", "estandar", "premium"]


class CreateCourseSchema(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str
    hashtags: str
    type: str
    exams: int = Field(gt=0)
    subscription: str
    location: str = Field(min_length=3, max_length=255)
    user_id: int
    profile_pic_url: str

    @validator("subscription")
    def validSubscriptionType(cls, subscription):
        subscription = subscription.lower()
        if subscription not in SUBSCRIPTION_TYPES:
            raise InvalidSubscriptionType(SUBSCRIPTION_TYPES)
        return subscription


class DeleteCourseSchema(BaseModel):
    id: int
    user_id: int


class EditCourseInfoSchema(BaseModel):
    user_id: int
    name: str = Field(min_length=1, max_length=255)
    description: str
    location: str = Field(min_length=3, max_length=255)
    hashtags: str


class CollaboratorSchema(BaseModel):
    user_id: int
    id: int


class RemoveCollaboratorSchema(BaseModel):
    user_id: int
    user_to_remove: int
    id: int


class UserSchema(BaseModel):
    user_id: int


class FavCourseSchema(BaseModel):
    user_id: int
    id: int


class CollaborationRequest(BaseModel):
    email_collaborator: str
    user_id: int
    id: int


class SubscriberGradesSchema(BaseModel):
    user_id: int
    course_id: int
    grades: List[str]


class NotificationSchema(BaseModel):
    title: str
    body: str
    user_id: int


class SummarySchema(BaseModel):
    course_id: int
    user_id: int


class MultimediaSchema(BaseModel):
    title: str
    url: str
    user_id: int
    tag: Optional[str] = ""
