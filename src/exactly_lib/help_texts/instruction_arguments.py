from exactly_lib.help_texts import type_system
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a

HERE_DOCUMENT = a.Named('HERE-DOCUMENT')

REG_EX = a.Named('REG-EX')

SYMBOL_REFERENCE = a.Named('SYMBOL-REFERENCE')

PATH_SYNTAX_ELEMENT_NAME = 'PATH'
PATH_ARGUMENT = a.Named(PATH_SYNTAX_ELEMENT_NAME)
FILE_ARGUMENT = a.Named('FILE')
DIR_ARGUMENT = a.Named('DIR')

RELATIVITY_ARGUMENT = a.Named('RELATIVITY')

OPTIONAL_RELATIVITY_ARGUMENT_USAGE = a.Single(a.Multiplicity.OPTIONAL,
                                              RELATIVITY_ARGUMENT)
NEGATION_ARGUMENT_STR = '!'

SELECTOR_ARGUMENT = a.Named(type_system.FILE_SELECTOR_VALUE)
SELECTION_OPTION = a.option(long_name='selection',
                            argument=SELECTOR_ARGUMENT.name)
SELECTION = a.Named('SELECTION')

LINES_TRANSFORMATION_ARGUMENT = a.Named('TRANSFORMATION')
WITH_TRANSFORMED_CONTENTS_OPTION_NAME = a.OptionName(long_name='transformation')
WITH_TRANSFORMED_CONTENTS_OPTION = option_syntax.option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME)
TRANSFORMATION_OPTION = a.Option(WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                 argument=type_system.LINES_TRANSFORMER_VALUE)
