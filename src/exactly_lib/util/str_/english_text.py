from typing import Sequence

OR_WORD = ' or '


def or_sequence(elements: Sequence[str]) -> str:
    if len(elements) == 0:
        return ''

    if len(elements) == 1:
        return elements[0]

    comma_sep = ', '.join(elements[:-1])
    return OR_WORD.join((comma_sep, elements[-1]))
