from exactly_lib.definitions import instruction_arguments
from exactly_lib.util.cli_syntax.elements import argument as a

EMPTINESS_CHECK_ARGUMENT = 'empty'

RECURSIVE_OPTION = a.option('recursive')

NON_RECURSIVE_MODEL_NAME = 'non-recursive'

MIN_DEPTH_OPTION = a.option('min-depth',
                            argument=instruction_arguments.INTEGER_ARGUMENT.name)

MAX_DEPTH_OPTION = a.option('max-depth',
                            argument=instruction_arguments.INTEGER_ARGUMENT.name)

DIR_FILE_SET_OPTIONS = a.Named('DIR-CONTENTS-OPTIONS')
