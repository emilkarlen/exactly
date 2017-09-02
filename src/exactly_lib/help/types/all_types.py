from exactly_lib.help.types.type_ import string


def all_types() -> list:
    return [
        string.DOCUMENTATION,
    ]


NAME_2_TYPE_DOC = dict(map(lambda x: (x.singular_name(), x), all_types()))
