from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib_test.common.test_resources import instruction_documentation as instr_doc
from exactly_lib_test.section_document.test_resources.instruction_parser import ParserThatGives


def single_instruction_setup(instruction_name: str,
                             instruction: Instruction) -> SingleInstructionSetup:
    return single_instruction_setup_for_parser(instruction_name,
                                               ParserThatGives(instruction))


def single_instruction_setup_for_parser(instruction_name: str,
                                        parser: InstructionParser) -> SingleInstructionSetup:
    return SingleInstructionSetup(parser,
                                  instr_doc.instruction_documentation(instruction_name))
