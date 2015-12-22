from shellcheck_lib.document import model
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.help.instruction_description import Description


class SingleInstructionSetup(SingleInstructionParser):
    def __init__(self,
                 parser: SingleInstructionParser,
                 description: Description):
        self._parser = parser
        self._description = description

    @property
    def description(self) -> Description:
        return self._description

    def apply(self, source: SingleInstructionParserSource) -> model.Instruction:
        return self._parser.apply(source)


class InstructionsSetup:
    def __init__(self,
                 config_instruction_set: dict,
                 setup_instruction_set: dict,
                 assert_instruction_set: dict,
                 cleanup_instruction_set: dict):
        """
        Each dictionary is a mapping: instruction-name -> SingleInstructionSetup.

        Each SingleInstructionSetup should parse and construct an instruction for
         the correct phase (of course). I.e., sub classes of Instruction.
        """
        self._config_instruction_set = config_instruction_set
        self._setup_instruction_set = setup_instruction_set
        self._assert_instruction_set = assert_instruction_set
        self._cleanup_instruction_set = cleanup_instruction_set

    @property
    def config_instruction_set(self) -> dict:
        return self._config_instruction_set

    @property
    def setup_instruction_set(self) -> dict:
        return self._setup_instruction_set

    @property
    def assert_instruction_set(self) -> dict:
        return self._assert_instruction_set

    @property
    def cleanup_instruction_set(self) -> dict:
        return self._cleanup_instruction_set

    @property
    def phase_and_instruction_set(self) -> list:
        """
        :return: [(Phase, dict)]
        """
        return [
            (phases.ANONYMOUS, self.config_instruction_set),
            (phases.SETUP, self.setup_instruction_set),
            (phases.ASSERT, self.assert_instruction_set),
            (phases.CLEANUP, self.cleanup_instruction_set),
        ]
