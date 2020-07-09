from typing import Tuple


class Name:
    def __init__(self,
                 singular: str,
                 plural: str):
        self._plural = plural
        self._singular = singular

    @staticmethod
    def new_with_plural_s(singular: str) -> 'Name':
        return Name(singular,
                    singular + 's')

    @property
    def singular(self) -> str:
        return self._singular

    @property
    def plural(self) -> str:
        return self._plural


class NumberOfItemsString:
    """Formatting of strings as: N item(s)"""

    def __init__(self, item_type_name: Name):
        self._item_type_name = item_type_name

    def of(self, num_items: int) -> str:
        if num_items == 1 or num_items == -1:
            item_name = self._item_type_name.singular
        else:
            item_name = self._item_type_name.plural

        return str(num_items) + ' ' + item_name


class NameWithGender(Name):
    SINGULAR = 'singular'
    PLURAL = 'plural'
    PLURAL_SHORT = 's'
    DETERMINED = 'determined'
    DETERMINATOR_WORD = 'determinator_word'
    DEFAULT = ''

    def __init__(self, determinator_word: str, singular: str, plural: str):
        super().__init__(singular, plural)
        self._determinator_word = determinator_word
        self._formats = {
            self.SINGULAR: singular,
            self.PLURAL: plural,
            self.PLURAL_SHORT: plural,
            self.DETERMINED: determinator_word + ' ' + singular,
            self.DETERMINATOR_WORD: determinator_word,
            self.DEFAULT: singular,
        }

    def __str__(self, *args, **kwargs):
        return self.singular

    def __format__(self, format_spec):
        try:
            return self._formats[format_spec]
        except KeyError:
            raise ValueError('Invalid word-with-gender format: "%s"' % format_spec)

    @property
    def singular_determined(self) -> str:
        return self._determinator_word + ' ' + self.singular

    @property
    def determinator_word(self) -> str:
        return self._determinator_word


def _init_cap__determined(det: str, word: str) -> Tuple[str, str]:
    return det.capitalize(), word


def _init_cap__undetermined(det: str, word: str) -> Tuple[str, str]:
    return det, word.capitalize()


def _upper_case(det: str, word: str) -> Tuple[str, str]:
    return det.upper(), word.upper()


class NameWithGenderWithFormatting(NameWithGender):
    SINGULAR = 'singular'
    PLURAL = 's'
    DETERMINED = 'a'
    DETERMINATOR_WORD = 'determinator_word'
    DEFAULT = ''

    FLAG_SEPARATOR = '/'
    QUOTED_FLAG = 'q'
    INIT_CAP_FLAG = 'u'
    UPPER_CASE_FLAG = 'U'

    _MODIFIERS_UNDETERMINED = {
        INIT_CAP_FLAG: _init_cap__undetermined,
        UPPER_CASE_FLAG: _upper_case,
    }

    _MODIFIERS_DETERMINED = {
        INIT_CAP_FLAG: _init_cap__determined,
        UPPER_CASE_FLAG: _upper_case,
    }

    def __init__(self,
                 name: NameWithGender,
                 quoting_begin: str = '"',
                 quoting_end: str = '"'):
        super().__init__(name.determinator_word,
                         name.singular,
                         name.plural)
        self._quoting_begin = quoting_begin
        self._quoting_end = quoting_end
        self._formats = {
            self.SINGULAR: name.singular,
            self.PLURAL: name.plural,
            self.DETERMINED: name.singular,
            self.DETERMINATOR_WORD: name.determinator_word,
            self.DEFAULT: name.singular,
        }

    @property
    def quoting_begin(self) -> str:
        return self._quoting_begin

    @property
    def quoting_end(self) -> str:
        return self._quoting_end

    def __str__(self, *args, **kwargs):
        return self.singular

    def __format__(self, format_spec: str) -> str:
        try:

            parts = format_spec.split(self.FLAG_SEPARATOR, 1)
            do_quote = False
            fmt = parts[0]

            det = self.determinator_word
            name_string = self._formats[fmt]

            modifiers = (self._MODIFIERS_DETERMINED
                         if fmt == self.DETERMINED
                         else self._MODIFIERS_UNDETERMINED)

            if len(parts) == 2:
                for flag in parts[1]:
                    if flag == self.QUOTED_FLAG:
                        do_quote = True
                    else:
                        det, name_string = modifiers[flag](det, name_string)
                if do_quote:
                    name_string = self.quoting_begin + name_string + self.quoting_end

            return (
                det + ' ' + name_string
                if fmt == self.DETERMINED
                else name_string
            )
        except KeyError:
            raise ValueError('Invalid name-with-gender format: "%s"' % format_spec)


def a_name(name: Name) -> NameWithGender:
    return NameWithGender('a', name.singular, name.plural)


def an_name(name: Name) -> NameWithGender:
    return NameWithGender('an', name.singular, name.plural)


def name_with_plural_s(singular: str) -> Name:
    return Name(singular,
                singular + 's')


def a_name_with_plural_s(singular: str) -> NameWithGender:
    return NameWithGender('a',
                          singular,
                          singular + 's'
                          )


def an_name_with_plural_s(singular: str) -> NameWithGender:
    return NameWithGender('an',
                          singular,
                          singular + 's'
                          )
