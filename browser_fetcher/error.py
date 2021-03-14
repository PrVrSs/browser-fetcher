import logging
from functools import wraps


logger = logging.getLogger(__name__)


def handle_error(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BrowserFetcherError as exc:
            logger.error(
                'Discarded: Request with following params %s;\nReason: %s', kwargs, str(exc))

    return wrapper


class BrowserFetcherError(Exception):
    pass


class RequestError(BrowserFetcherError):
    pass


class DownloadError(BrowserFetcherError):
    pass


class ValidateError(BrowserFetcherError):
    pass
