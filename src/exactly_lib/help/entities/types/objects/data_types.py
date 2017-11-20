from exactly_lib.help.entities.types.contents_structure import TypeDocumentation
from exactly_lib.help_texts.entity import types, syntax_element
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.textformat.structure.document import empty_contents

STRING_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                         types.STRING_TYPE_INFO,
                                         syntax_element.STRING_SYNTAX_ELEMENT,
                                         empty_contents())

LIST_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                       types.LIST_TYPE_INFO,
                                       syntax_element.LIST_SYNTAX_ELEMENT,
                                       empty_contents())

PATH_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                       types.PATH_TYPE_INFO,
                                       syntax_element.PATH_SYNTAX_ELEMENT,
                                       empty_contents())
