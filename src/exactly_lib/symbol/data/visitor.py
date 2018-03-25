from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.resolver_structure import DataValueResolver


class DataValueResolverVisitor:
    """
    Visitor of `DataValueResolver`
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
