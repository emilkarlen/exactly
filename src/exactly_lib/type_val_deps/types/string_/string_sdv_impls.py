from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.string_ import string_ddv as sv, strings_ddvs as csv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringFragmentSdv
from exactly_lib.type_val_deps.types.string_.strings_ddvs import StrValueTransformer, TransformedStringFragmentDdv, \
    StringDdvFragmentDdv
from exactly_lib.util.symbol_table import SymbolTable


class ConstantStringFragmentSdv(StringFragmentSdv):
    """
    A fragment that is a string constant.
    """

    def __init__(self, constant: str):
        self._constant = constant

    @property
    def is_string_constant(self) -> bool:
        return True

    @property
    def string_constant(self) -> str:
        return self._constant

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> sv.StringFragmentDdv:
        return csv.ConstantFragmentDdv(self._constant)


class SymbolStringFragmentSdv(StringFragmentSdv):
    """
    A fragment that represents a reference to a symbol.
    """

    def __init__(self, symbol_reference: SymbolReference):
        self._symbol_reference = symbol_reference

    @property
    def symbol_name(self) -> str:
        return self._symbol_reference.name

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_reference,

    def resolve(self, symbols: SymbolTable) -> sv.StringFragmentDdv:
        container = symbols.lookup(self._symbol_reference.name)
        assert isinstance(container, SymbolContainer), 'Value in SymTbl must be SymbolContainer'
        value_sdv = container.sdv
        assert isinstance(value_sdv, DataTypeSdv), 'Value must be a DataTypeSdv'
        value = value_sdv.resolve(symbols)
        if isinstance(value, sv.StringDdv):
            return csv.StringDdvFragmentDdv(value)
        elif isinstance(value, PathDdv):
            return csv.PathFragmentDdv(value)
        elif isinstance(value, ListDdv):
            return csv.ListFragmentDdv(value)
        else:
            raise TypeError('Not a {}: {}'.format(str(DataTypeSdv),
                                                  value))


class PathAsStringFragmentSdv(StringFragmentSdv):
    def __init__(self, path: PathSdv):
        self._path = path

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._path.references

    def resolve(self, symbols: SymbolTable) -> sv.StringFragmentDdv:
        return csv.PathFragmentDdv(self._path.resolve(symbols))


class ListAsStringFragmentSdv(StringFragmentSdv):
    def __init__(self, list_sdv: ListSdv):
        self._list_sdv = list_sdv

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._list_sdv.references

    def resolve(self, symbols: SymbolTable) -> sv.StringFragmentDdv:
        return csv.ListFragmentDdv(self._list_sdv.resolve(symbols))


class TransformedStringFragmentSdv(StringFragmentSdv):
    """
    A fragment who's string is transformed by a function.
    """

    def __init__(self,
                 string_sdv: StringFragmentSdv,
                 transformer: StrValueTransformer):
        self._string_sdv = string_sdv
        self._transformer = transformer

    @property
    def is_string_constant(self) -> bool:
        return self._string_sdv.is_string_constant

    @property
    def string_constant(self) -> str:
        return self._transformer(self._string_sdv.string_constant)

    def resolve(self, symbols: SymbolTable) -> sv.StringFragmentDdv:
        return TransformedStringFragmentDdv(StringDdvFragmentDdv(self._string_sdv.resolve(symbols)),
                                            self._transformer)

    @property
    def references(self) -> list:
        return self._string_sdv.references

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        return self.resolve(environment.symbols).value_of_any_dependency(environment)
