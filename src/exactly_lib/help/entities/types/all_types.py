from exactly_lib.help.entities.types.objects import data_types, logic_types
from exactly_lib.type_system.value_type import TypeCategory


def all_types() -> list:
    return [
        data_types.STRING_DOCUMENTATION,
        data_types.LIST_DOCUMENTATION,
        data_types.PATH_DOCUMENTATION,
        logic_types.LINE_MATCHER_DOCUMENTATION,
        logic_types.FILE_MATCHER_DOCUMENTATION,
        logic_types.STRING_TRANSFORMER_DOCUMENTATION,
        logic_types.PROGRAM_DOCUMENTATION,
    ]


NAME_2_TYPE_DOC = dict(map(lambda x: (x.singular_name(), x), all_types()))


def type_docs_of_type_category(category: TypeCategory, type_doc_list: list) -> list:
    return list(filter(lambda type_doc: type_doc.type_category is category,
                       type_doc_list))
