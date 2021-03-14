import logging
import platform
from enum import Enum, Flag
from operator import itemgetter
from pathlib import Path
from shutil import unpack_archive
from typing import List, Optional

from more_itertools import last

from ..error import handle_error
from ..provider import Provider

from .model import Artifact, Index, validate


logger = logging.getLogger(__name__)

QUEUE = 'queue'
INDEX = 'index'


class Product(Enum):
    MOBILE = 'mobile'
    DESKTOP = 'firefox'


class Branch(Enum):
    pass


class BuildValue(int):

    def __new__(cls, value, name):
        self = super().__new__(cls, value)
        self.__flag_name__ = name
        return self


class Build(Flag):

    COVERAGE = C = BuildValue(1, 'ccov')
    FUZZING = F = BuildValue(2, 'fuzzing')
    ASAN = A = BuildValue(4, 'asan')
    TSAN = T = BuildValue(8, 'tsan')
    VALGRIND = BuildValue(16, 'valgrind')
    DEBUG = D = BuildValue(32, 'debug')
    OPTIMIZED = O = BuildValue(64, 'opt')

    def _members(self, value: int):
        for member in self.__class__:
            if value & member.value:
                value &= ~member.value

                yield member.value.__flag_name__

    def __repr__(self):
        return '-'.join(self._members(self.value))

    __str__ = object.__str__

# globals().update(Build.__members__)


class Platform:
    """Class representing target OS and CPU, and how it maps to a Gecko mozconfig"""

    SUPPORTED = {
        'Darwin': {
            'x86_64': 'macosx64',
        },
        'Linux': {
            'x86_64': 'linux64',
            'x86': 'linux',
        },
        'Windows': {
            'x86_64': 'win64',
            'arm64': 'win64-aarch64',
        },
    }

    CPU_ALIASES = {
        'ARM64': 'arm64',
        'AMD64': 'x86_64',
        'aarch64': 'arm64',
        'i686': 'x86',
        'x64': 'x86_64',
    }

    def __init__(self):
        system = platform.system()
        machine = platform.machine()
        machine = self.CPU_ALIASES.get(machine, machine)

        self.system = self.SUPPORTED[system][machine]


INSTANCE: str = 'https://firefox-ci-tc.services.mozilla.com/api'


class API:

    def __init__(self, provider: Provider):
        self._provider = provider

    @handle_error
    @validate
    def task(self, namespace: str, product: str, system: str, flags: str) -> Optional[Index]:
        return self._provider.do_request(
            f'{INSTANCE}/{INDEX}/v1/task/{namespace}.{product}.{system}-{flags}')

    @handle_error
    @validate(key=itemgetter('artifacts'))
    def artifacts(self, task_id: str) -> Optional[List[Artifact]]:
        return self._provider.do_request(
            f'{INSTANCE}/{QUEUE}/v1/task/{task_id}/artifacts')

    @handle_error
    def download(self, task_id: str, name: str, output: str) -> None:
        return self._provider.download(
            url=f'{INSTANCE}/{QUEUE}/v1/task/{task_id}/artifacts/{name}', output=output)

    # def queue(self, task_id: str):
    #     return self._provider.do_request(f'{INSTANCE}/{QUEUE}/v1/task/{task_id}')


def create_api(provider: Provider) -> API:
    return API(provider=provider)


class Firefox:

    def __init__(self):
        self._api = create_api(Provider())

    def __getattr__(self, item):
        return getattr(self._api, item)


def download(flags: Build, product: str, branch: str, build: str, output: str) -> None:
    firefox = Firefox()

    task = firefox.task(
        namespace=f'gecko.v2.{branch}.{build}',
        product=product,
        system=Platform().system,
        flags=str(flags)
    )

    if task is None:
        return

    artifacts = firefox.artifacts(task_id=task.task_id)
    tar = [item.name for item in artifacts if item.content_type == 'application/x-bzip2'][0]

    file_name = last(tar.split('/'))
    firefox.download(task_id=task.task_id, name=tar, output=str(Path(output) / file_name))

    logger.info('Unpack archive: %s', file_name)
    unpack_archive(str(Path(output) / file_name), extract_dir=str(Path(output)))
    logger.info('Successfully unpacked')
