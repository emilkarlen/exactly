from shellcheck_lib.document import model
from shellcheck_lib.general import line_source
from shellcheck_lib.instructions.instruction_parser_for_single_phase import SingleInstructionParser


class Description:
    def __init__(self,
                 single_line_description: str):
        self.__single_line_description = single_line_description

    @property
    def single_line_description(self) -> str:
        return self.__single_line_description


class SingleInstructionSetup(SingleInstructionParser):
    def __init__(self,
                 parser: SingleInstructionParser,
                 description: Description):
        self._parser = parser
        self._description = description

    @property
    def description(self) -> Description:
        return self._description

    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> model.Instruction:
        return self._parser.apply(source, instruction_argument)


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
