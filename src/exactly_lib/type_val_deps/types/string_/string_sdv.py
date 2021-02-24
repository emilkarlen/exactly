from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.types.string_ import string_ddv as sv
from exactly_lib.util.symbol_table import SymbolTable


class StringFragmentSdv(DataTypeSdv):
    """
    A part of the value of a StringSdv.
    """

    @property
    def is_string_constant(self) -> bool:
        return False

    @property
    def string_constant(self) -> str:
        """
        :raises ValueError: This object does not represent a string constant
        :rtype str
        """
        raise ValueError('The object is not a string constant')

    def resolve(self, symbols: SymbolTable) -> sv.StringFragmentDdv:
        raise NotImplementedError()


class StringSdv(DataTypeSdv):
    """
    SDV who's resolved value is of type `ValueType.STRING` / :class:`StringDdv`
    """

    def __init__(self, fragment_sdvs: Sequence[StringFragmentSdv]):
        self._fragment_sdvs = fragment_sdvs

    def resolve(self, symbols: SymbolTable) -> sv.StringDdv:
        fragments = [fr.resolve(symbols)
                     for fr in self._fragment_sdvs]
        return sv.StringDdv(tuple(fragments))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references(self._fragment_sdvs)

    @property
    def has_fragments(self) -> bool:
        """
        Whether there are any fragments or not.
        :return:
        """
        return len(self._fragment_sdvs) != 0

    @property
    def fragments(self) -> Sequence[StringFragmentSdv]:
        """
        The sequence of fragments that makes up the value.

        The resolved value is the concatenation of all fragments.
        """
        return self._fragment_sdvs

    @property
    def is_string_constant(self) -> bool:
        """
        Tells if the object does not depend on any symbols
        """
        return all(map(lambda x: x.is_string_constant, self._fragment_sdvs))

    @property
    def string_constant(self) -> str:
        """
        Precondition: is_string_constant

        :return: The constant string that this object represents
        """
        fragments = [fragment_sdv.string_constant
                     for fragment_sdv in self._fragment_sdvs]
        return ''.join(fragments)

    def __str__(self):
        return str(type(self))
