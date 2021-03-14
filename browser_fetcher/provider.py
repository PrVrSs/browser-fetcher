import logging
from collections import ChainMap
from typing import Any, ClassVar, Dict, Iterable, Optional

import requests
from more_itertools import last
from requests import RequestException, Response
from tqdm import tqdm

from .error import DownloadError, RequestError


logger = logging.getLogger(__name__)


class Provider:

    _default_params: ClassVar[Dict[str, Any]] = {
        'stream': False,
        'timeout': 10,
    }

    def __init__(self):
        self._session = requests.session()

    def do_request(self, url: str, **kwargs: Any) -> Response:
        logger.debug('URL: %s', url)

        try:
            response = self._session.get(url, **ChainMap(kwargs, self._default_params))
            response.raise_for_status()

            return response
        except RequestException as exc:
            raise RequestError(exc)

    def download(self, url: str, output: str) -> None:
        response = self.do_request(url, stream=True)

        save(
            content=response.iter_content(chunk_size=1024 * 1024),
            desc=last(url.split('/')),
            total=int(response.headers.get('content-length', 0)),
            output=output,
        )

    def __del__(self):
        self._session.close()


def save(content: Iterable[bytes], desc: str, total: int, output: str) -> None:
    tqdm_config = {
        'miniters': 1,
        'desc': desc,
        'total': total,
        'ascii': True,
        'colour': 'green',

    }

    try:
        with tqdm.wrapattr(open(output, 'wb'), 'write', **tqdm_config) as file:
            for chunk in content:
                file.write(chunk)
    except Exception as exc:  # pylint: disable=broad-except
        raise DownloadError(exc)
