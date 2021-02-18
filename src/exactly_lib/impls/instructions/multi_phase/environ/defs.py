from exactly_lib.definitions import instruction_arguments, logic
from exactly_lib.util.cli_syntax.elements import argument as a

UNSET_IDENTIFIER = 'unset'
ASSIGNMENT_IDENTIFIER = instruction_arguments.ASSIGNMENT_OPERATOR
VAR_NAME_ELEMENT = 'NAME'
VAR_VALUE_ELEMENT = 'VALUE'
PHASE_SPEC_ELEMENT = 'PHASE-SPEC'

PHASE_SPEC__OPTION_NAME = a.OptionName('of')

PHASE_SPEC__ACT = 'act'
PHASE_SPEC__NON_ACT = logic.NOT_OPERATOR_NAME + PHASE_SPEC__ACT
