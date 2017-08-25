from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR, HARD_QUOTE_CHAR


class Surrounded:
    def __init__(self, delimiter: str, surrounded: str):
        self.surrounded = surrounded
        self.delimiter = delimiter

    def __str__(self):
        return self.delimiter + self.surrounded + self.delimiter


def surrounded_by_soft_quotes(surrounded: str) -> Surrounded:
    return Surrounded(SOFT_QUOTE_CHAR, surrounded)


def surrounded_by_hard_quotes(surrounded: str) -> Surrounded:
    return Surrounded(HARD_QUOTE_CHAR, surrounded)
