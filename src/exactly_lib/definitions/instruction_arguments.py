from exactly_lib.definitions.entity import types
from exactly_lib.definitions.path import REL_SYMBOL_OPTION_NAME
from exactly_lib.util.cli_syntax.elements import argument as a

SYMBOL_SYNTAX_ELEMENT_NAME = 'SYMBOL'

SYMBOL_NAME_ARGUMENT = a.Named('SYMBOL-NAME')
SYMBOL_REFERENCE_ARGUMENT = a.Named('SYMBOL-REFERENCE')

REL_SYMBOL_OPTION = a.Option(REL_SYMBOL_OPTION_NAME,
                             SYMBOL_NAME_ARGUMENT.name)

COMMAND_ARGUMENT = a.Named('SHELL-COMMAND-LINE')

HERE_DOCUMENT = a.Named('HERE-DOCUMENT')

STRING = a.Named(types.STRING_TYPE_INFO.syntax_element_name)

INTEGER_ARGUMENT = a.Named('INTEGER')

REG_EX = a.Named('REG-EX')

GLOB_PATTERN = a.Named('GLOB-PATTERN')

SYMBOL_REFERENCE = a.Named('SYMBOL-REFERENCE')

PATH_SYNTAX_ELEMENT_NAME = types.PATH_TYPE_INFO.syntax_element_name
PATH_ARGUMENT = a.Named(PATH_SYNTAX_ELEMENT_NAME)
FILE_ARGUMENT = a.Named('FILE')

DIR_WITHOUT_RELATIVITY_OPTIONS_ARGUMENT = a.Named('DIRECTORY')

RELATIVITY_ARGUMENT = a.Named('RELATIVITY')

OPTIONAL_RELATIVITY_ARGUMENT_USAGE = a.Single(a.Multiplicity.OPTIONAL,
                                              RELATIVITY_ARGUMENT)

MATCHER_ARGUMENT = a.Named(types.FILE_MATCHER_TYPE_INFO.syntax_element_name)

LINE_MATCHER = a.Named(types.LINE_MATCHER_TYPE_INFO.syntax_element_name)

ASSIGNMENT_OPERATOR = '='

DESTINATION_PATH_ARGUMENT = a.Named('DESTINATION')
SOURCE_PATH_ARGUMENT = a.Named('SOURCE')
