import pathlib
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_visitor import WStrRenderingTypeSdvPseudoVisitor
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv, PathPartSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.symbol_table import SymbolTable


class SdvThatIsIdenticalToReferencedPathOrWithStringValueAsSuffix(PathSdv):
    """
    A file-ref from a symbol reference, that can be either a string or a file-ref
    """

    def __init__(self,
                 path_or_string_symbol: SymbolReference,
                 suffix_sdv: PathPartSdv,
                 default_relativity: RelOptionType,
                 ):
        self._path_or_string_symbol = path_or_string_symbol
        self._suffix_sdv = suffix_sdv
        self.default_relativity = default_relativity

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        symbol_value_2_path = _WStrRenderingValueSymbol2PathResolverVisitor(self._suffix_sdv,
                                                                            self.default_relativity,
                                                                            symbols)
        container = symbols.lookup(self._path_or_string_symbol.name)
        assert isinstance(container, SymbolContainer), 'Implementation consistency/SymbolContainer'
        sdv = container.sdv
        assert isinstance(sdv, DataTypeSdv), 'Implementation consistency/DataTypeSdv'
        return symbol_value_2_path.visit(sdv)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self._path_or_string_symbol] + list(self._suffix_sdv.references)


class _WStrRenderingValueSymbol2PathResolverVisitor(WStrRenderingTypeSdvPseudoVisitor[PathDdv]):
    def __init__(self,
                 suffix_sdv: PathPartSdv,
                 default_relativity: RelOptionType,
                 symbols: SymbolTable,
                 ):
        self.suffix_sdv = suffix_sdv
        self.symbols = symbols
        self.default_relativity = default_relativity

    def visit_path(self, value: PathSdv) -> PathDdv:
        path = value.resolve(self.symbols)
        suffix_str = self.suffix_sdv.resolve(self.symbols).value()
        if not suffix_str:
            return path
        suffix_str = suffix_str.lstrip('/')
        return path_ddvs.stacked(path, path_ddvs.constant_path_part(suffix_str))

    def visit_string(self, value: StringSdv) -> PathDdv:
        string_ddv = value.resolve(self.symbols)
        first_suffix_str = string_ddv.value_when_no_dir_dependencies()
        following_suffix_str = self.suffix_sdv.resolve(self.symbols).value()
        path_str = first_suffix_str + following_suffix_str
        path = pathlib.Path(path_str)
        if path.is_absolute():
            return path_ddvs.absolute_file_name(path_str)
        else:
            return path_ddvs.of_rel_option(self.default_relativity,
                                           path_ddvs.constant_path_part(path_str))

    def visit_list(self, value: ListSdv) -> PathDdv:
        raise ValueError('Impossible to convert a list to a path')
