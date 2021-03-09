from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel

from ..utils import to_camel_case


class Index(BaseModel):

    namespace: str
    task_id: str
    rank: int
    data: Dict[Any, Any]
    expires: datetime

    class Config:
        alias_generator = to_camel_case
