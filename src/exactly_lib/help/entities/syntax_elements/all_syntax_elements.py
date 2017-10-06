from exactly_lib.help.entities.syntax_elements.element import here_document, regex, glob_pattern

ALL_SYNTAX_ELEMENT_DOCS = [
    here_document.DOCUMENTATION,
    regex.DOCUMENTATION,
    glob_pattern.DOCUMENTATION,
]

NAME_2_SYNTAX_ELEMENT_DOC = dict(map(lambda x: (x.singular_name(), x), ALL_SYNTAX_ELEMENT_DOCS))
