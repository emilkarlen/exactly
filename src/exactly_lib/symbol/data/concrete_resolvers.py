from exactly_lib.symbol.data import string_resolver, list_resolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.resolver_structure import DataValueResolver


class SymbolValueResolverVisitor:
    """
    Visitor of `SymbolValueResolver`
    """

    def visit(self, value: DataValueResolver):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileRefResolver):
            return self._visit_file_ref(value)
        if isinstance(value, StringResolver):
            return self._visit_string(value)
        if isinstance(value, ListResolver):
            return self._visit_list(value)
        raise TypeError('Unknown {}: {}'.format(DataValueResolver, str(value)))

    def _visit_string(self, value: StringResolver):
        raise NotImplementedError()

    def _visit_file_ref(self, value: FileRefResolver):
        raise NotImplementedError()

    def _visit_list(self, value: ListResolver):
        raise NotImplementedError()


def list_constant(str_list: list) -> ListResolver:
    return ListResolver([list_resolver.string_element(string_resolver.string_constant(s))
                         for s in str_list])
