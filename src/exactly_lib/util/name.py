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

    _MODIFIERS = {
        INIT_CAP_FLAG: str.capitalize,
        UPPER_CASE_FLAG: str.upper,
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
            self.DETERMINED: name.determinator_word + ' ' + name.singular,
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
            ret_val = self._formats[parts[0]]
            if len(parts) == 2:
                for flag in parts[1]:
                    if flag == self.QUOTED_FLAG:
                        do_quote = True
                    else:
                        ret_val = self._MODIFIERS[flag](ret_val)
                if do_quote:
                    ret_val = self.quoting_begin + ret_val + self.quoting_end
            return ret_val
        except KeyError:
            raise ValueError('Invalid word-with-gender format: "%s"' % format_spec)


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
