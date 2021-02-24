from typing import List, Sequence

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity.all_entity_types import BUILTIN_SYMBOL_ENTITY_TYPE_NAMES
from exactly_lib.definitions.entity.builtins import name_and_ref_target
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.textformat.structure.document import SectionContents


class BuiltinSymbolDocumentation(EntityDocumentation):
    def __init__(self,
                 value_type: ValueType,
                 symbol_name: str,
                 single_line_description_str: str,
                 description: SectionContents,
                 see_also: Sequence[SeeAlsoTarget] = (),
                 ):
        super().__init__(
            name_and_ref_target(symbol_name, single_line_description_str)
        )
        self._value_type = value_type
        self._description = description
        self._see_also = see_also

    @property
    def value_type(self) -> ValueType:
        return self._value_type

    @property
    def description(self) -> SectionContents:
        return self._description

    @property
    def see_also(self) -> Sequence[SeeAlsoTarget]:
        return self._see_also


def builtin_symbols_help(builtin_documentations: List[BuiltinSymbolDocumentation]) -> EntityTypeHelp:
    return EntityTypeHelp(BUILTIN_SYMBOL_ENTITY_TYPE_NAMES,
                          builtin_documentations)
