from functools import reduce
from operator import or_
from pathlib import Path
from typing import Optional, Union

import click
from click import Context, Option, Parameter

from .instance import Build, download


def build_flag(_: Context, param: Union[Option, Parameter], value: str) -> Optional[Build]:
    if value is False:
        return None

    return Build[param.name.upper()]


def _prepare_output_dir(_: Context, __: Union[Option, Parameter], value: str) -> str:
    Path(value).resolve().mkdir(parents=True, exist_ok=True)

    return value


@click.command(name='firefox')
@click.option(
    '-d/-o', '--debug/--optimized',
    callback=lambda _, __, value: Build.DEBUG if value is True else Build.OPTIMIZED,
    default=False,
    help='Get debug builds symbols (default=optimized).'
)
@click.option(
    '-a', '--asan',
    is_flag=True,
    callback=build_flag,
    help='Download AddressSanitizer builds.'
)
@click.option(
    '-t', '--tsan',
    is_flag=True,
    callback=build_flag,
    help='Download ThreadSanitizer builds.'
)
@click.option(
    '-f', '--fuzzing',
    is_flag=True,
    callback=build_flag,
    help='Download --enable-fuzzing builds.'
)
@click.option(
    '-c', '--coverage',
    is_flag=True,
    callback=build_flag,
    help='Download --coverage builds.'
)
@click.option(
    '-v', '--valgrind',
    is_flag=True,
    callback=build_flag,
    help='Download Valgrind builds.'
)
@click.option(
    '--branch',
    type=click.Choice(['mozilla-central', 'mozilla-release', 'mozilla-beta']),
    default='mozilla-central',
    help='Branch (default=mozilla-central).'
)
@click.option(
    '--build',
    type=click.Choice(['latest']),
    default='latest',
    help='Build (default=latest).'
)
@click.option(
    '--target',
    type=click.Choice(['firefox', 'js']),
    default='firefox',
    help='Target (default=firefox).'
)
@click.option(
    '-o', '--output',
    type=click.Path(file_okay=False, resolve_path=True),
    callback=_prepare_output_dir,
    default='.output',
    help='',
)
def cli(
        debug: Build,
        asan: Optional[Build],
        tsan: Optional[Build],
        fuzzing: Optional[Build],
        coverage: Optional[Build],
        valgrind: Optional[Build],
        branch: str,
        build: str,
        target: str,
        output: str,
) -> None:
    download(
        flags=reduce(or_, filter(None, [debug, asan, tsan, fuzzing, coverage, valgrind])),
        branch=branch,
        build=build,
        product=target,
        output=output,
    )
