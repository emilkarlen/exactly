from exactly_lib.definitions import doc_format
from exactly_lib.util.textformat.structure import structures as docs

DESCRIPTION__HEADER__UPPERCASE = docs.text('DESCRIPTION')
DESCRIPTION__HEADER__CAPITALIZED = docs.text('Description')

NOTES__HEADER__UPPERCASE = docs.text('NOTES')
NOTES__HEADER__CAPITALIZED = docs.text('Notes')
NOTE_LINE_HEADER = 'Note:'

OUTCOME__HEADER__UPPERCASE = docs.text('OUTCOME')

SYNOPSIS_TEXT = docs.text('SYNOPSIS')

WHERE_PARA = docs.para(doc_format.text_as_header('where'))
FORMS_PARA = docs.para(doc_format.text_as_header('Forms:'))
