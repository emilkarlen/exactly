from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.symbol.value_structure import SymbolValueResolver


class SymbolValueResolverVisitor:
    """
    Visitor of `Value`
    """

    def visit(self, value: SymbolValueResolver):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileRefResolver):
            return self._visit_file_ref(value)
        if isinstance(value, StringResolver):
            return self._visit_string(value)
        raise TypeError('Unknown {}: {}'.format(SymbolValueResolver, str(value)))

    def _visit_string(self, value: StringResolver):
        raise NotImplementedError()

    def _visit_file_ref(self, value: FileRefResolver):
        raise NotImplementedError()
