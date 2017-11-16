from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase
from exactly_lib.help_texts.entity.all_entity_types import BUILTIN_SYMBOL_ENTITY_TYPE_NAMES
from exactly_lib.help_texts.entity.builtin import name_and_ref_target
from exactly_lib.type_system.value_type import ValueType, TypeCategory, VALUE_TYPE_2_TYPE_CATEGORY
from exactly_lib.util.textformat.structure.document import SectionContents


class BuiltinSymbolDocumentation(EntityDocumentationBase):
    def __init__(self,
                 value_type: ValueType,
                 symbol_name: str,
                 single_line_description_str: str,
                 description: SectionContents):
        super().__init__(
            name_and_ref_target(symbol_name, single_line_description_str)
        )
        self._value_type = value_type
        self._description = description

    @property
    def type_category(self) -> TypeCategory:
        return VALUE_TYPE_2_TYPE_CATEGORY[self.value_type]

    @property
    def value_type(self) -> ValueType:
        return self._value_type

    @property
    def description(self) -> SectionContents:
        return self._description


def builtin_symbols_help(builtin_documentations: iter) -> EntitiesHelp:
    """
    :param builtin_documentations: [BuiltinSymbolDocumentation]
    """
    return EntitiesHelp(BUILTIN_SYMBOL_ENTITY_TYPE_NAMES,
                        builtin_documentations)
