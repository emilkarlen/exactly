from exactly_lib.common.instruction_setup import SingleInstructionSetup
from . import parser, doc


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(parser.Parser(),
                                  doc.TheInstructionDocumentation(instruction_name))
