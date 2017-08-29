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
