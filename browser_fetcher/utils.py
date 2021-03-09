from more_itertools import value_chain


def to_camel_case(string: str) -> str:
    first, *tail = string.split('_')

    return ''.join(value_chain(first, map(str.title, tail)))
