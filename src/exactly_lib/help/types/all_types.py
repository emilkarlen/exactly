from exactly_lib.help.types.type_ import data_types


def all_types() -> list:
    return [
        data_types.STRING_DOCUMENTATION,
        data_types.LIST_DOCUMENTATION,
        data_types.PATH_DOCUMENTATION,
    ]


NAME_2_TYPE_DOC = dict(map(lambda x: (x.singular_name(), x), all_types()))
