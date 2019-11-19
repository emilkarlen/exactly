from typing import TypeVar, Generic

from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv

T = TypeVar('T')


class DataTypeSdvPseudoVisitor(Generic[T]):
    """
    Visitor of `DataTypeSdv`
    """

    def visit(self, value: DataTypeSdv) -> T:
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, PathSdv):
            return self.visit_path(value)
        if isinstance(value, StringSdv):
            return self.visit_string(value)
        if isinstance(value, ListSdv):
            return self.visit_list(value)
        raise TypeError('Unknown {}: {}'.format(DataTypeSdv, str(value)))

    def visit_string(self, value: StringSdv) -> T:
        raise NotImplementedError()

    def visit_path(self, value: PathSdv) -> T:
        raise NotImplementedError()

    def visit_list(self, value: ListSdv) -> T:
        raise NotImplementedError()
