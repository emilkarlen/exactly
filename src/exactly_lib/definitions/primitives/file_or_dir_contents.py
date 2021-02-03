from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.util.cli_syntax.elements import argument as a

EMPTINESS_CHECK_ARGUMENT = 'is-empty'

RECURSIVE_OPTION = a.option('recursive')

NON_RECURSIVE_MODEL_NAME = 'non-recursive'

MIN_DEPTH_OPTION = a.option('min-depth',
                            argument=syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name)

MAX_DEPTH_OPTION = a.option('max-depth',
                            argument=syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name)

DIR_FILE_SET_OPTIONS = a.Named('DIR-CONTENTS-OPTIONS')
