import logging
from collections import ChainMap
from typing import Any, ClassVar, Dict, Iterable, Optional

import requests
from requests import RequestException, Response
from tqdm import tqdm


logger = logging.getLogger(__name__)


class Provider:

    _default_params: ClassVar[Dict[str, Any]] = {
        'stream': False,
        'timeout': 10,
    }

    def __init__(self):
        self._session = requests.session()

    def do_request(self, url: str, **kwargs) -> Optional[Response]:
        try:
            response = self._session.get(url, **ChainMap(kwargs, self._default_params))
            response.raise_for_status()
        except RequestException as exc:
            logger.exception(exc)
            return

        return response

    def download(self, url: str, output: str) -> bool:
        if response := self.do_request(url, stream=True):
            return save(
                content=response.iter_content(chunk_size=1024 * 1024),
                desc=url,
                total=int(response.headers.get('content-length', 0)),
                output=output,
            )

        return False

    def __del__(self):
        self._session.close()


def save(content: Iterable[bytes], desc: str, total: int, output: str) -> bool:
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

        return True
    except Exception as exc:
        logger.exception(exc)
        return False
