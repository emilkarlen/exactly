from exactly_lib.section_document.syntax import section_header


class SectionName:
    """
    Name of a section in a section-document, with formats for str.format().

    Supports a number of formats, used as format-specifiers:

    $ 'The section {my_section:emphasis} ...'.format(my_section)
    """

    SYNTAX = 'syntax'
    PLAIN = 'plain'
    EMPHASIS = 'emphasis'
    DEFAULT = ''

    def __init__(self, name: str):
        self._name = name
        self._formats = {
            self.SYNTAX: section_header(name),
            self.PLAIN: name,
            self.EMPHASIS: emphasis(name),
            self.DEFAULT: emphasis(name),
        }

    @property
    def plain(self) -> str:
        return self._formats[self.PLAIN]

    @property
    def emphasis(self) -> str:
        return self._formats[self.EMPHASIS]

    @property
    def syntax(self) -> str:
        return self._formats[self.SYNTAX]

    def __str__(self, *args, **kwargs):
        return self._name

    def __format__(self, format_spec):
        try:
            return self._formats[format_spec]
        except KeyError:
            raise ValueError('Invalid section format: "%s"' % format_spec)


class InstructionName:
    """
    Name of an instruction in a section-document, with formats for str.format().

    Supports a number of formats, used as format-specifiers:

    $ 'The section {my_instruction:emphasis} ...'.format(my_section)

    The supported formats are the same as the getter methods.
    """

    PLAIN = 'plain'
    EMPHASIS = 'emphasis'
    DEFAULT = ''

    def __init__(self, name: str):
        self._name = name
        self._formats = {
            self.PLAIN: name,
            self.EMPHASIS: emphasis(name),
            self.DEFAULT: emphasis(name),
        }

    @property
    def plain(self) -> str:
        return self._formats[self.PLAIN]

    @property
    def emphasis(self) -> str:
        return self._formats[self.EMPHASIS]

    def __str__(self, *args, **kwargs):
        return self._name

    def __format__(self, format_spec):
        try:
            return self._formats[format_spec]
        except KeyError:
            raise ValueError('Invalid section format: "%s"' % format_spec)


class AnyInstructionNameDictionary(dict):
    """
    A virtual dictionary that gives an InstructionName for any key.
    """

    def __getitem__(self, key):
        return InstructionName(key)


def cli_option(s: str) -> str:
    return '"' + s + '"'


def cli_argument_option_string(option: str) -> str:
    return '"' + option + '"'


def emphasis(s: str) -> str:
    return '"' + s + '"'


def term(s: str) -> str:
    return '"' + s + '"'


def concept(s: str) -> str:
    return '"' + s + '"'


def entity(name: str) -> str:
    return '"' + name + '"'


def program_name(name: str) -> str:
    return '"' + name + '"'
