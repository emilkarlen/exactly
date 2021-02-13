from exactly_lib.definitions import instruction_arguments, logic
from exactly_lib.util.cli_syntax.elements import argument as a

UNSET_IDENTIFIER = 'unset'
ASSIGNMENT_IDENTIFIER = instruction_arguments.ASSIGNMENT_OPERATOR
VAR_NAME_ELEMENT = 'NAME'

PHASE_SPEC__OPTION = a.OptionName('of')

PHASE_SPEC__ACT = 'act'
PHASE_SPEC__NON_ACT = logic.NOT_OPERATOR_NAME + PHASE_SPEC__ACT
