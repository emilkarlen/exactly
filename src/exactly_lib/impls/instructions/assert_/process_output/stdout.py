from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import misc_texts
from exactly_lib.impls.instructions.assert_.utils.file_contents import parse_instruction
from exactly_lib.impls.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from .impl import out_err_file, doc


def setup_for_stdout(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(instruction_name),
        doc.for_std_output_file(instruction_name, misc_texts.STDOUT),
    )


def parser(instruction_name: str) -> AssertPhaseInstructionParser:
    return parse_instruction.Parser(instruction_name,
                                    out_err_file.Parser(ProcOutputFile.STDOUT))
