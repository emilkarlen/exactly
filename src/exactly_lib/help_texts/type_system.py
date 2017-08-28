PATH_TYPE = 'path'
STRING_TYPE = 'string'
LIST_TYPE = 'list'

FILE_SELECTOR_TYPE = 'file-selector'

STRING_VALUE = 'STRING'
LIST_ELEMENT = 'ELEMENT'


def syntax_of_type_name_in_text(type_name: str) -> str:
    return '"' + type_name + '"'
