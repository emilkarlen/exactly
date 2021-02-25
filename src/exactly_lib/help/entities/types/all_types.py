from typing import List

from exactly_lib.definitions.type_system import TypeCategory
from exactly_lib.help.entities.types.contents_structure import TypeDocumentation
from exactly_lib.help.entities.types.objects import data_types, logic_types


def all_types() -> List[TypeDocumentation]:
    return [
        data_types.STRING_DOCUMENTATION,
        data_types.LIST_DOCUMENTATION,
        data_types.PATH_DOCUMENTATION,
        data_types.FILES_CONDITION_DOCUMENTATION,

        logic_types.INTEGER_MATCHER_DOCUMENTATION,
        logic_types.LINE_MATCHER_DOCUMENTATION,
        logic_types.FILE_MATCHER_DOCUMENTATION,
        logic_types.FILES_MATCHER_DOCUMENTATION,
        logic_types.STRING_SOURCE_DOCUMENTATION,
        logic_types.STRING_MATCHER_DOCUMENTATION,
        logic_types.STRING_TRANSFORMER_DOCUMENTATION,
        logic_types.PROGRAM_DOCUMENTATION,
    ]


NAME_2_TYPE_DOC = dict(map(lambda x: (x.singular_name(), x), all_types()))


def type_docs_of_type_category(category: TypeCategory,
                               type_docs: List[TypeDocumentation]) -> List[TypeDocumentation]:
    return list(filter(lambda type_doc: type_doc.type_category is category,
                       type_docs))
