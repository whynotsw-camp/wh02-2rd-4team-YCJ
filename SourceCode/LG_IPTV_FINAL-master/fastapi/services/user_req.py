from pydantic import BaseModel
from typing import List

class UserRequest(BaseModel):
    categories: List[str]
    userInfo: dict
