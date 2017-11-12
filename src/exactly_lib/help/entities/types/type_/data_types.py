from exactly_lib.help.entities.types.contents_structure import TypeDocumentation
from exactly_lib.help_texts.entity import types
from exactly_lib.type_system.value_type import TypeCategory

STRING_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                         types.STRING_CONCEPT_INFO)

LIST_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                       types.LIST_CONCEPT_INFO)

PATH_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                       types.PATH_CONCEPT_INFO)
