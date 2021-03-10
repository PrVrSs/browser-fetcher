from datetime import datetime
from functools import update_wrapper
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


class Artifact(BaseModel):

    storage_type: str
    name: str
    expires: datetime
    content_type: str

    class Config:
        alias_generator = to_camel_case


def get_validation_cls(func):
    return func.__annotations__['return'].__args__[0]


_validate_null = object()


def validate(__func__=_validate_null, key=None):
    if __func__ is not _validate_null:
        return update_wrapper(_validate_wrapper(__func__), __func__)

    def decorating_function(user_function):
        return update_wrapper(_validate_wrapper(user_function, key), user_function)

    return decorating_function


def _validate_wrapper(user_function, key=lambda _: _):

    validation_cls = get_validation_cls(user_function)

    def wrapper(*args, **kwargs):
        if result := user_function(*args, **kwargs):
            prepared = key(result.json())

            if getattr(validation_cls, '_name', '') == 'List':
                return [validation_cls.__args__[0](**item) for item in prepared]

            return validation_cls(**prepared)

    return wrapper
