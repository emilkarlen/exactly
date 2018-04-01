from exactly_lib.symbol import symbol_syntax
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer


class SymbolReferenceArgument(ArgumentElementRenderer):
    """
    Formats a symbol name as a symbol reference, if used as value in str.format()
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self, *args, **kwargs):
        return symbol_syntax.symbol_reference_syntax_for_name(self.name)
