from exactly_lib.help_texts import type_system
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import Quantifier

HERE_DOCUMENT = a.Named('HERE-DOCUMENT')

STRING = a.Named('STRING')

REG_EX = a.Named('REG-EX')

GLOB_PATTERN = a.Named('GLOB-PATTERN')

SYMBOL_REFERENCE = a.Named('SYMBOL-REFERENCE')

PATH_SYNTAX_ELEMENT_NAME = 'PATH'
PATH_ARGUMENT = a.Named(PATH_SYNTAX_ELEMENT_NAME)
FILE_ARGUMENT = a.Named('FILE')
DIR_ARGUMENT = a.Named('DIR')

RELATIVITY_ARGUMENT = a.Named('RELATIVITY')

OPTIONAL_RELATIVITY_ARGUMENT_USAGE = a.Single(a.Multiplicity.OPTIONAL,
                                              RELATIVITY_ARGUMENT)
NEGATION_ARGUMENT_STR = '!'

MATCHER_ARGUMENT = a.Named(type_system.FILE_MATCHER_VALUE)
SELECTION_OPTION = a.option(long_name='selection',
                            argument=MATCHER_ARGUMENT.name)
SELECTION = a.Named('SELECTION')

LINE_MATCHER = a.Named('LINE-MATCHER')

LINES_TRANSFORMER_ARGUMENT = a.Named(type_system.LINES_TRANSFORMER_VALUE)

LINES_TRANSFORMATION_ARGUMENT = a.Named('TRANSFORMATION')
WITH_TRANSFORMED_CONTENTS_OPTION_NAME = a.OptionName(long_name='transformation')
WITH_TRANSFORMED_CONTENTS_OPTION = option_syntax.option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME)
TRANSFORMATION_OPTION = a.Option(WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                 argument=type_system.LINES_TRANSFORMER_VALUE)

ALL_QUANTIFIER_ARGUMENT = 'every'
EXISTS_QUANTIFIER_ARGUMENT = 'any'

QUANTIFICATION_SEPARATOR_ARGUMENT = ':'

QUANTIFIER_ARGUMENTS = {
    Quantifier.ALL: ALL_QUANTIFIER_ARGUMENT,
    Quantifier.EXISTS: EXISTS_QUANTIFIER_ARGUMENT,
}

DESTINATION_PATH_ARGUMENT = a.Named('DESTINATION')
SOURCE_PATH_ARGUMENT = a.Named('SOURCE')
