from exactly_lib.help.types.contents_structure import TypeDocumentation
from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.entity import types


class StringTypeDocumentation(TypeDocumentation):
    def __init__(self):
        super().__init__(type_system.STRING_TYPE,
                         types.STRING_CONCEPT_INFO)


DOCUMENTATION = StringTypeDocumentation()
