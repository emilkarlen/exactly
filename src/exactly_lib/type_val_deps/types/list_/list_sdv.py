from typing import Sequence, Iterable, List, Optional

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.string_ import strings_ddvs as ddvs
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.symbol_table import SymbolTable


class ElementSdv:
    """
    An element of a list.
    """

    @property
    def symbol_reference_if_is_symbol_reference(self) -> Optional[SymbolReference]:
        """
        :returns: None if this element is not a single-symbol-reference element ,
        else the reference.
        """
        raise NotImplementedError()

    @property
    def references(self) -> Sequence[SymbolReference]:
        """
        Values in the symbol table used by this object.
        """
        raise NotImplementedError()

    def resolve(self, symbols: SymbolTable) -> List[StringDdv]:
        """Gives the list of string values that this element represents"""
        raise NotImplementedError()


class StringElementSdv(ElementSdv):
    """ An element that is a string. """

    def __init__(self, string_sdv: StringSdv):
        self._string_sdv = string_sdv

    @property
    def symbol_reference_if_is_symbol_reference(self) -> SymbolReference:
        """
        :returns: None if this element is not a single-symbol-reference element ,
        else the reference.
        """
        return None

    @property
    def references(self) -> Sequence[SymbolReference]:
        return tuple(self._string_sdv.references)

    def resolve(self, symbols: SymbolTable) -> List[StringDdv]:
        return [self._string_sdv.resolve(symbols)]


class SymbolReferenceElementSdv(ElementSdv):
    """ An element that is a reference to a symbol. """

    def __init__(self, symbol_reference: SymbolReference):
        self._symbol_reference = symbol_reference

    @property
    def symbol_reference_if_is_symbol_reference(self) -> SymbolReference:
        return self._symbol_reference

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_reference,

    def resolve(self, symbols: SymbolTable) -> List[StringDdv]:
        container = symbols.lookup(self._symbol_reference.name)
        ddv = container.sdv.resolve(symbols)
        if isinstance(ddv, StringDdv):
            return [ddv]
        if isinstance(ddv, PathDdv):
            return [ddvs.string_ddv_of_single_path(ddv)]
        if isinstance(ddv, ListDdv):
            return list(ddv.string_elements)
        raise TypeError('Unknown Symbol Value: ' + str(ddv))


class ListSdv(DataTypeSdv):
    """
    Resolver who's resolved value is of type `ValueType.LIST` / :class:`ListDdv`
    """

    def __init__(self, elements: Iterable[ElementSdv]):
        self._elements = tuple(elements)

    @property
    def elements(self) -> Sequence[ElementSdv]:
        return self._elements

    @property
    def references(self) -> Sequence[SymbolReference]:
        ret_val = []
        for string_sdv in self._elements:
            ret_val.extend(string_sdv.references)
        return ret_val

    def resolve(self, symbols: SymbolTable) -> ListDdv:
        value_elements = []
        for sdv_element in self._elements:
            value_elements.extend(sdv_element.resolve(symbols))
        return ListDdv(value_elements)
