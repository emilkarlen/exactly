from typing import Mapping

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.impls.types.files_source.defs import ModificationType, FileType
from exactly_lib.util.cli_syntax.elements import argument as a

COPY_CONTENTS_OF_EXISTING_DIR = 'dir-contents-of'

FILE_LIST_BEGIN = reserved_words.BRACE_BEGIN
FILE_LIST_END = reserved_words.BRACE_END

FILE_LIST_END__FOR_FORMAT_STRINGS = reserved_words.BRACE__END__FOR_FORMAT_STRINGS

FILE_MATCHER_SEPARATOR = ':'

FILE_NAME = instruction_arguments.FILE_NAME_STRING
FILE_NAME__ARG = a.Single(a.Multiplicity.MANDATORY, FILE_NAME)

FILE_TYPE_SE_STR = 'FILE-TYPE'
FILE_SPEC__SE_STR = 'FILE-SPEC'

REGULAR_FILE_TOKEN = instruction_names.NEW_FILE_INSTRUCTION_NAME
DIRECTORY_TOKEN = instruction_names.NEW_DIR_INSTRUCTION_NAME

FILE_TYPE_TOKENS = {
    FileType.REGULAR: REGULAR_FILE_TOKEN,
    FileType.DIR: DIRECTORY_TOKEN,
}

EXPLICIT_CREATE = instruction_arguments.ASSIGNMENT_OPERATOR
EXPLICIT_APPEND = instruction_arguments.APPEND_OPERATOR

MODIFICATION_VARIANT_TOKENS: Mapping[ModificationType, str] = {
    ModificationType.CREATE: EXPLICIT_CREATE,
    ModificationType.APPEND: EXPLICIT_APPEND,
}

EXPLICIT_CONTENTS_CONFIG: Mapping[str, ModificationType] = {
    item[1]: item[0]
    for item in MODIFICATION_VARIANT_TOKENS.items()
}

MODIFICATION_ARGUMENT__ASSIGN = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(EXPLICIT_CREATE))

MODIFICATION_ARGUMENT__APPEND = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(EXPLICIT_APPEND))
