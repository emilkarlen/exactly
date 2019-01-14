from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import types
from exactly_lib.instructions.assert_ import define_symbol as define_symbol__assert
from exactly_lib.instructions.before_assert import define_symbol as define_symbol__before_assert
from exactly_lib.instructions.cleanup import define_symbol as define_symbol__cleanup
from exactly_lib.instructions.setup import define_symbol as define_symbol__setup
from exactly_lib.processing.instruction_setup import InstructionsSetup

DEF_INSTRUCTION_NAME = 'define'

INSTRUCTION_SETUP = InstructionsSetup(
    setup_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol__setup.setup(DEF_INSTRUCTION_NAME)
    },
    before_assert_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol__before_assert.setup(DEF_INSTRUCTION_NAME)
    },
    assert_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol__assert.setup(DEF_INSTRUCTION_NAME)
    },
    cleanup_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol__cleanup.setup(DEF_INSTRUCTION_NAME)
    },
)


def define_string(symbol_name: str, value: str) -> str:
    return ' '.join([
        DEF_INSTRUCTION_NAME,
        types.STRING_TYPE_INFO.identifier,
        symbol_name,
        instruction_arguments.ASSIGNMENT_OPERATOR,
        value,
    ])
