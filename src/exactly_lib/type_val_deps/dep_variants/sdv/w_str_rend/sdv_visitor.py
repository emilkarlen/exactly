from typing import TypeVar, Generic

from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv

T = TypeVar('T')


class WStrRenderingTypeSdvPseudoVisitor(Generic[T]):
    """Visitor of all SDV:s that can be rendered as a string"""

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
