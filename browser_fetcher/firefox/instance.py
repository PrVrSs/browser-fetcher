import logging
import platform
from enum import Enum, IntFlag, auto
from typing import Callable, ClassVar, Optional
from functools import wraps

from browser_fetcher.downloader import Provider
from browser_fetcher.firefox.model import Index


logger = logging.getLogger(__name__)


class Product(Enum):
    MOBILE = 'mobile'
    DESKTOP = 'firefox'


class Branch(Enum):
    pass


class Build(IntFlag):

    ccov = COVERAGE = C = auto()
    fuzzing = FUZZING = F = auto()
    asan = ASAN = A = auto()
    tsan = TSAN = T = auto()
    valgrind = VALGRIND = V = auto()
    debug = DEBUG = D = auto()

    def _members(self, value: int):
        for member in self.__class__:
            if value & member.value:
                value &= ~member.value
                yield f'-{member.name}'

    def __repr__(self):
        return ''.join(self._members(self.value))

    __str__ = object.__str__

# globals().update(Build.__members__)


class PureFirefox:
    pass


class WindowsFirefox(PureFirefox):
    pass


class DarwinFirefox(PureFirefox):
    pass


class LinuxFirefox(PureFirefox):
    pass


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


def get_validation_cls(func):
    """TODO: fix it"""
    return func.__annotations__['return'].__args__[0]


def validate(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if result := func(*args, **kwargs):
            return get_validation_cls(func)(**result.json())

    return wrapper


class API:

    instance: ClassVar[Callable[[str, str], str]] = (
        'https://firefox-ci-tc.services.mozilla.com/api/{action}/v1/task/{path}').format

    task_path: ClassVar[Callable[[str, str, str, str], str]] = (
        '{namespace}.{product}.{system}{flags}').format

    artifacts: ClassVar[Callable[[str], str]] = '{task_id}/artifacts'.format

    artifact: ClassVar[Callable[[str, str], str]] = '{task_id}/artifacts/{name}'.format

    def __init__(self, provider: Provider):
        self._provider = provider

    @validate
    def task(self, namespace: str, product: str, system: str, flags: str) -> Optional[Index]:
        return self._provider.do_request(
            self.instance(
                action='index',
                path=self.task_path(
                    namespace=namespace,
                    product=product,
                    system=system,
                    flags=flags,
                )
            )
        )

    @validate
    def queue(self, task_id: str):
        return self._provider.do_request(self.instance(action='queue', path=task_id))

    @validate
    def artifacts(self, task_id: str):
        return self._provider.do_request(
            self.instance(action='queue', path=self.artifacts(task_id=task_id)))

    def download(self, task_id: str, name: str, output: str) -> bool:
        return self._provider.download(
            url=self.instance(action='queue', path=self.artifact(task_id=task_id, name=name)),
            output=output,
        )


def create_api(provider: Provider) -> API:
    return API(provider=provider)


class Firefox:

    def __init__(self):
        self._api = create_api(Provider())

    def __getattr__(self, item):
        return getattr(self._api, item)


core = Firefox()


product = 'firefox'
branch = 'mozilla-central'
namespace = "gecko.v2." + branch + ".latest"

t = core.task(
    namespace=namespace,
    product=product,
    system=Platform().system,
    flags=str(Build.ASAN | Build.DEBUG)
)

print(t)
