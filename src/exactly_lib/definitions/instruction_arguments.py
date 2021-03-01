from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.path import REL_SYMBOL_OPTION_NAME
from exactly_lib.util.cli_syntax.elements import argument as a

ASSIGNMENT_OPERATOR = '='

SYMBOL_SYNTAX_ELEMENT_NAME = 'SYMBOL'

REL_SYMBOL_OPTION = a.Option(REL_SYMBOL_OPTION_NAME,
                             syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.singular_name)

RELATIVITY_ARGUMENT = a.Named('RELATIVITY')

OPTIONAL_RELATIVITY_ARGUMENT_USAGE = a.Single(a.Multiplicity.OPTIONAL,
                                              RELATIVITY_ARGUMENT)

FILE_ARGUMENT = a.Named('FILE')

DIR_WITHOUT_RELATIVITY_OPTIONS_ARGUMENT = a.Named('DIRECTORY')

DESTINATION_PATH_ARGUMENT = a.Named('DESTINATION')
SOURCE_PATH_ARGUMENT = a.Named('SOURCE')

FILE_NAME_STRING = a.Named('FILE-NAME')

FILE_NAME_STRING__SINGLE_MANDATORY = a.Single(a.Multiplicity.MANDATORY,
                                              FILE_NAME_STRING)
