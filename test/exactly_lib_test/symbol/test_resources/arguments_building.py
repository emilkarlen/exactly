from typing import Sequence

from exactly_lib.symbol import symbol_syntax
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString


class SymbolReferenceArgument(ArgumentElementsRenderer):
    """
    Formats a symbol name as a symbol reference, if used as value in str.format()
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self, *args, **kwargs):
        return symbol_syntax.symbol_reference_syntax_for_name(self.name)

    @property
    def elements(self) -> Sequence[WithToString]:
        return [self]
