class Name:
    def __init__(self,
                 singular: str,
                 plural: str):
        self._plural = plural
        self._singular = singular

    @property
    def singular(self) -> str:
        return self._singular

    @property
    def plural(self) -> str:
        return self._plural


class NameWithGender(Name):
    def __init__(self, determinator_word: str, singular: str, plural: str):
        super().__init__(singular, plural)
        self._determinator_word = determinator_word

    @property
    def singular_determined(self) -> str:
        return self._determinator_word + ' ' + self.singular

    @property
    def determinator_word(self) -> str:
        return self._determinator_word


def a_name(name: Name) -> NameWithGender:
    return NameWithGender('a', name.singular, name.plural)


def an_name(name: Name) -> NameWithGender:
    return NameWithGender('an', name.singular, name.plural)


def name_with_plural_s(singular: str) -> Name:
    return Name(singular,
                singular + 's')
