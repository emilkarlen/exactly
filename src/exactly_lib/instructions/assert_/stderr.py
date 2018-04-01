from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils.file_contents import parse_instruction, stdout_stderr
from exactly_lib.instructions.assert_.utils.file_contents import stdout_stderr as utils
from exactly_lib.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.test_case_file_structure import sandbox_directory_structure


def setup_for_stderr(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(),
        utils.TheInstructionDocumentation(instruction_name,
                                          sandbox_directory_structure.RESULT_FILE__STDERR))


def parser() -> AssertPhaseInstructionParser:
    return parse_instruction.Parser(
        utils.Parser(
            stdout_stderr.ActComparisonActualFileForStdFileBase(
                sandbox_directory_structure.RESULT_FILE__STDERR)))
