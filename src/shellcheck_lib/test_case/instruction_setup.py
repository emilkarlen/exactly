from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.sections.common import TestCaseInstruction


class SingleInstructionSetup(SingleInstructionParser):
    def __init__(self,
                 parser: SingleInstructionParser,
                 description: Description):
        self._parser = parser
        self._description = description

    @property
    def description(self) -> Description:
        return self._description

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        return self._parser.apply(source)


def instruction_set_from_name_and_setup_constructor_list(name_and_setup_pair_list: list) -> dict:
    return dict(map(_name_and_setup, name_and_setup_pair_list))


class InstructionsSetup(tuple):
    def __new__(cls,
                config_instruction_set: dict,
                setup_instruction_set: dict,
                assert_instruction_set: dict,
                before_assert_instruction_set: dict,
                cleanup_instruction_set: dict):
        """
        Each dictionary is a mapping: instruction-name -> SingleInstructionSetup.

        Each SingleInstructionSetup should parse and construct an instruction for
         the correct phase (of course). I.e., sub classes of Instruction.
        """
        return tuple.__new__(cls, (config_instruction_set,
                                   setup_instruction_set,
                                   assert_instruction_set,
                                   before_assert_instruction_set,
                                   cleanup_instruction_set))

    @property
    def config_instruction_set(self) -> dict:
        return self[0]

    @property
    def setup_instruction_set(self) -> dict:
        return self[1]

    @property
    def before_assert_instruction_set(self) -> dict:
        return self[2]

    @property
    def assert_instruction_set(self) -> dict:
        return self[3]

    @property
    def cleanup_instruction_set(self) -> dict:
        return self[4]


def _name_and_setup(instruction_name__and__setup_constructor) -> (str, SingleInstructionSetup):
    instruction_name = instruction_name__and__setup_constructor[0]
    setup_constructor = instruction_name__and__setup_constructor[1]
    return (instruction_name,
            setup_constructor(instruction_name))
