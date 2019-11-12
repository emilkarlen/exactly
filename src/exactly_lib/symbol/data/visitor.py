from typing import TypeVar, Generic

from exactly_lib.symbol.data.data_value_resolver import DataValueResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.path_resolver import PathResolver
from exactly_lib.symbol.data.string_resolver import StringResolver

T = TypeVar('T')


class DataValueResolverPseudoVisitor(Generic[T]):
    """
    Visitor of `DataValueResolver`
    """

    def visit(self, value: DataValueResolver) -> T:
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, PathResolver):
            return self.visit_path(value)
        if isinstance(value, StringResolver):
            return self.visit_string(value)
        if isinstance(value, ListResolver):
            return self.visit_list(value)
        raise TypeError('Unknown {}: {}'.format(DataValueResolver, str(value)))

    def visit_string(self, value: StringResolver) -> T:
        raise NotImplementedError()

    def visit_path(self, value: PathResolver) -> T:
        raise NotImplementedError()

    def visit_list(self, value: ListResolver) -> T:
        raise NotImplementedError()
