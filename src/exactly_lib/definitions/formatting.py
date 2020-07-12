from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.section_document.syntax import section_header
from exactly_lib.util.cli_syntax import short_and_long_option_syntax, option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.str_.name import NameWithGender, NameWithGenderWithFormatting


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
            raise ValueError('Invalid instruction format: "%s"' % format_spec)


class AnyInstructionNameDictionary(dict):
    """
    A virtual dictionary that gives an InstructionName for any key.
    """

    def __getitem__(self, key):
        return InstructionName(str(key).replace('_', '-'))


def cli_option(s: str) -> str:
    return '"' + s + '"'


def cli_option_argument(option_name: short_and_long_option_syntax.ShortAndLongOptionName) -> str:
    return cli_argument_option_string(short_and_long_option_syntax.long_syntax(option_name.long))


def cli_argument_option_string(option: str) -> str:
    return '"' + option + '"'


def argument_option(name: a.OptionName) -> str:
    return option_syntax.option_syntax(name)


def emphasis(s: str) -> str:
    return '"' + s + '"'


def term(s: str) -> str:
    return '"' + s + '"'


def concept(s: str) -> str:
    return '"' + s + '"'


def concept_name_with_formatting(name: NameWithGender) -> NameWithGenderWithFormatting:
    return _common_name_with_formatting(name)


def type_name_with_formatting(name: NameWithGender) -> NameWithGenderWithFormatting:
    return _common_name_with_formatting(name)


def concept_(x: SingularNameAndCrossReferenceId) -> str:
    return concept(x.singular_name)


def conf_param(s: str) -> str:
    return '"' + s + '"'


def conf_param_(x: SingularNameAndCrossReferenceId) -> str:
    return conf_param(x.singular_name)


def entity(name: str) -> str:
    return '"' + name + '"'


def entity_(name: SingularNameAndCrossReferenceId) -> str:
    return entity(name.singular_name)


def entity_name_with_formatting(name: NameWithGender) -> NameWithGenderWithFormatting:
    return _common_name_with_formatting(name)


def symbol_type(name: str) -> str:
    return '"' + name + '"'


def symbol_type_(name: SingularNameAndCrossReferenceId) -> str:
    return symbol_type(name.singular_name)


def program_name(name: str) -> str:
    return name.capitalize()


def string_constant(constant: str) -> str:
    return '"' + constant + '"'


def keyword(keyword: str) -> str:
    return '"' + keyword + '"'


def syntax_element(human_readable_name: str) -> str:
    """
    Transforms a name with space and lowercase letters
    to a string suitable as syntax element
    """
    return human_readable_name.upper().replace(' ', '-')


def syntax_element_(name: SingularNameAndCrossReferenceId) -> str:
    return syntax_element(name.singular_name)


def misc_name_with_formatting(name: NameWithGender) -> NameWithGenderWithFormatting:
    return _common_name_with_formatting(name)


def _common_name_with_formatting(name: NameWithGender) -> NameWithGenderWithFormatting:
    return NameWithGenderWithFormatting(name,
                                        quoting_begin='"',
                                        quoting_end='"')
