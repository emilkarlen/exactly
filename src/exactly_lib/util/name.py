class Name(tuple):
    def __new__(cls,
                singular: str,
                plural: str):
        return tuple.__new__(cls, (singular, plural))

    @property
    def singular(self) -> str:
        return self[0]

    @property
    def plural(self) -> str:
        return self[1]


def name_with_plural_s(singular: str) -> Name:
    return Name(singular,
                singular + 's')
