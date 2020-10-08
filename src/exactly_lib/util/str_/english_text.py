from typing import Sequence

OR_WORD = ' or '
AND_WORD = ' and '


def and_sequence(elements: Sequence[str]) -> str:
    return sequence(AND_WORD, elements)


def or_sequence(elements: Sequence[str]) -> str:
    return sequence(OR_WORD, elements)


def sequence(last_separator: str, elements: Sequence[str]) -> str:
    if len(elements) == 0:
        return ''

    if len(elements) == 1:
        return elements[0]

    comma_sep = ', '.join(elements[:-1])
    return last_separator.join((comma_sep, elements[-1]))
