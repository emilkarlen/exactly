from exactly_lib.help.syntax_elements.element import here_document

ALL_SYNTAX_ELEMENT_DOCS = [
    here_document.DOCUMENTATION,
]

NAME_2_SYNTAX_ELEMENT_DOC = dict(map(lambda x: (x.singular_name(), x), ALL_SYNTAX_ELEMENT_DOCS))
