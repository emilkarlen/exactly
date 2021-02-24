from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference, ObjectWithSymbolReferences
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.util.symbol_table import SymbolTable


class PathSdv(DataTypeSdv):
    """
    Resolver who's resolved value is of type `ValueType.PATH` / :class:`PathDdv`
    """

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    def __str__(self):
        return str(type(self))


class PathPartSdv(ObjectWithSymbolReferences):
    """
    The relative path that follows the root path of the `PathDdv`.
    """

    def resolve(self, symbols: SymbolTable) -> PathPartDdv:
        raise NotImplementedError()

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError()
