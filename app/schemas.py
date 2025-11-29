from pydantic import BaseModel


class ReviewResponse(BaseModel):
    id: int
    author_name: str
    rating: int
    text: str
    date_custom: str
    avatar_filename: str
    source: str

    class Config:
        from_attributes = True
