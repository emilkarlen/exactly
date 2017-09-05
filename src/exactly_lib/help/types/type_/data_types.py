from exactly_lib.help.types.contents_structure import TypeDocumentation
from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.entity import types
from exactly_lib.type_system.value_type import ElementType

STRING_DOCUMENTATION = TypeDocumentation(ElementType.SYMBOL,
                                         type_system.STRING_TYPE,
                                         types.STRING_CONCEPT_INFO)

LIST_DOCUMENTATION = TypeDocumentation(ElementType.SYMBOL,
                                       type_system.LIST_TYPE,
                                       types.LIST_CONCEPT_INFO)

PATH_DOCUMENTATION = TypeDocumentation(ElementType.SYMBOL,
                                       type_system.PATH_TYPE,
                                       types.PATH_CONCEPT_INFO)
