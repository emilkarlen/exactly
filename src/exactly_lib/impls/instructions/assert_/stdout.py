from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.assert_.utils.file_contents import parse_instruction
from exactly_lib.impls.instructions.assert_.utils.file_contents import stdout_stderr as utils
from exactly_lib.impls.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.tcfs import sds
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


def setup_for_stdout(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(instruction_name),
        utils.TheInstructionDocumentation(instruction_name,
                                          sds.RESULT_FILE__STDOUT))


def parser(instruction_name: str) -> AssertPhaseInstructionParser:
    return parse_instruction.Parser(instruction_name,
                                    utils.Parser(ProcOutputFile.STDOUT))