_EXPECTED_HEADER = 'Expected : '
_FOUND_HEADER = 'Found    : '


def unexpected_lines(expected: str, found: str) -> str:
    return '\n'.join([
        _EXPECTED_HEADER + expected,
        _FOUND_HEADER + found,
    ])
