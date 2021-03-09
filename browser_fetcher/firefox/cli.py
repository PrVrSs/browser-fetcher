import click


@click.command(name='firefox')
@click.option(
    '-d', '--debug',
    is_flag=True,
    type=bool,
    help='Get debug builds w/ symbols (default=optimized).'
)
@click.option(
    '-a', '--asan',
    is_flag=True,
    type=bool,
    help='Download AddressSanitizer builds.'
)
@click.option(
    '-a', '--asan',
    is_flag=True,
    type=bool,
    help='Download AddressSanitizer builds.'
)
@click.option(
    '-t', '--tsan',
    is_flag=True,
    help='Download ThreadSanitizer builds.'
)
@click.option(
    '-f', '--fuzzing',
    is_flag=True,
    type=bool,
    help='Download --enable-fuzzing builds.'
)
@click.option(
    '-c', '--coverage',
    is_flag=True,
    type=bool,
    help='Download --coverage builds.'
)
@click.option(
    '-v', '--valgrind',
    is_flag=True,
    type=bool,
    help='Download Valgrind builds.'
)
def cli(
        debug: bool,
        asan: bool,
        tsan: bool,
        fuzzing: bool,
        coverage: bool,
        valgrind: bool,
) -> None:
    pass
