from datetime import datetime
from functools import update_wrapper
from typing import Any, Callable, Dict, Union

from pydantic import BaseModel, ValidationError

from ..error import ValidateError
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


def validate(__func__: Union[object, Callable[[Any], Any]] = _validate_null, key: Any = None):

    def decorating_function(user_function):
        return update_wrapper(_validate_wrapper(user_function, key), user_function)

    if __func__ is _validate_null:
        return decorating_function

    return update_wrapper(_validate_wrapper(__func__), __func__)


def _validate_wrapper(user_function, key=lambda _: _):

    validation_cls = get_validation_cls(user_function)

    def wrapper(*args, **kwargs):
        result = user_function(*args, **kwargs)
        prepared = key(result.json())

        if getattr(validation_cls, '_name', '') == 'List':
            return [_validate(validation_cls.__args__[0], item) for item in prepared]

        return _validate(validation_cls, prepared)

    return wrapper


def _validate(model, data):
    try:
        return model(**data)
    except ValidationError as exc:
        raise ValidateError(exc)
