from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import types
from exactly_lib.instructions.setup import define_symbol
from exactly_lib.processing.instruction_setup import InstructionsSetup

DEF_INSTRUCTION_NAME = 'define'

INSTRUCTION_SETUP = InstructionsSetup(
    setup_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol.setup(DEF_INSTRUCTION_NAME)
    }
)


def define_string(symbol_name: str, value: str) -> str:
    return ' '.join([
        DEF_INSTRUCTION_NAME,
        types.STRING_TYPE_INFO.identifier,
        symbol_name,
        instruction_arguments.ASSIGNMENT_OPERATOR,
        value,
    ])
