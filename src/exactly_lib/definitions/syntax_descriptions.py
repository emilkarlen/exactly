"""Simple syntax descriptions that are needed in more than one place"""
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.util.str_.name import a_name_with_plural_s, NameWithGenderWithFormatting

_SYMBOLS_ARE_SUBSTITUTED_IN = 'Any {} appearing in {} is substituted.'
_SYMBOLS_ARE_NOT_SUBSTITUTED_IN = 'Any {} appearing in {} is NOT substituted.'

SYMBOL_NAME_SYNTAX_DESCRIPTION = 'A combination of alphanumeric characters and underscores.'

SOFT_QUOTE_NAME = NameWithGenderWithFormatting(a_name_with_plural_s('soft quote'))
HARD_QUOTE_NAME = NameWithGenderWithFormatting(a_name_with_plural_s('hard quote'))


def symbols_are_substituted_in(element: str) -> str:
    return _SYMBOLS_ARE_SUBSTITUTED_IN.format(
        syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
        element
    )


def symbols_are_not_substituted_in(element: str) -> str:
    return _SYMBOLS_ARE_NOT_SUBSTITUTED_IN.format(
        syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
        element
    )
