from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.file_ref import REL_SYMBOL_OPTION_NAME
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import Quantifier

SYMBOL_SYNTAX_ELEMENT_NAME = 'SYMBOL'

SYMBOL_NAME_ARGUMENT = a.Named('SYMBOL-NAME')
SYMBOL_REFERENCE_ARGUMENT = a.Named('SYMBOL-REFERENCE')

REL_SYMBOL_OPTION = a.Option(REL_SYMBOL_OPTION_NAME,
                             SYMBOL_NAME_ARGUMENT.name)

COMMAND_ARGUMENT = a.Named('SHELL-COMMAND-LINE')
PROGRAM_ARGUMENT = a.Named('PROGRAM')

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
NEGATION_ARGUMENT_STR = '!'

MATCHER_ARGUMENT = a.Named(types.FILE_MATCHER_TYPE_INFO.syntax_element_name)
SELECTION_OPTION = a.option(long_name='selection',
                            argument=MATCHER_ARGUMENT.name)
SELECTION = a.Named('SELECTION')

LINE_MATCHER = a.Named(types.LINE_MATCHER_TYPE_INFO.syntax_element_name)

LINES_TRANSFORMER_ARGUMENT = a.Named(types.LINES_TRANSFORMER_TYPE_INFO.syntax_element_name)

LINES_TRANSFORMATION_ARGUMENT = a.Named('TRANSFORMATION')
WITH_TRANSFORMED_CONTENTS_OPTION_NAME = a.OptionName(long_name='transformed-by')
WITH_TRANSFORMED_CONTENTS_OPTION = option_syntax.option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME)
TRANSFORMATION_OPTION = a.Option(WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                 argument=types.LINES_TRANSFORMER_TYPE_INFO.syntax_element_name)

ASSIGNMENT_OPERATOR = '='

ALL_QUANTIFIER_ARGUMENT = 'every'
EXISTS_QUANTIFIER_ARGUMENT = 'any'

QUANTIFICATION_SEPARATOR_ARGUMENT = ':'

QUANTIFIER_ARGUMENTS = {
    Quantifier.ALL: ALL_QUANTIFIER_ARGUMENT,
    Quantifier.EXISTS: EXISTS_QUANTIFIER_ARGUMENT,
}

DESTINATION_PATH_ARGUMENT = a.Named('DESTINATION')
SOURCE_PATH_ARGUMENT = a.Named('SOURCE')
