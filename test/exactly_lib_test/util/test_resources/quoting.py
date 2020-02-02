from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR, HARD_QUOTE_CHAR


class Surrounded:
    def __init__(self,
                 before: str,
                 after: str,
                 surrounded: str,
                 ):
        self.after = after
        self.before = before
        self.surrounded = surrounded

    @staticmethod
    def with_identical(before_and_after: str, surrounded: str) -> 'Surrounded':
        return Surrounded(before_and_after, before_and_after, surrounded)

    def __str__(self):
        return self.before + self.surrounded + self.after


def surrounded_by_soft_quotes(surrounded: str) -> Surrounded:
    return Surrounded.with_identical(SOFT_QUOTE_CHAR, surrounded)


def surrounded_by_soft_quotes_str(surrounded: str) -> str:
    return str(Surrounded.with_identical(SOFT_QUOTE_CHAR, surrounded))


def surrounded_by_hard_quotes(surrounded: str) -> Surrounded:
    return Surrounded.with_identical(HARD_QUOTE_CHAR, surrounded)


def surrounded_by_hard_quotes_str(surrounded: str) -> str:
    return str(Surrounded.with_identical(HARD_QUOTE_CHAR, surrounded))
