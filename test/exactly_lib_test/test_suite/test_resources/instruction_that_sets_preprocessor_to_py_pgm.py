import sys

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib_test.common.test_resources import instruction_setup


def setup(instruction_name: str) -> SingleInstructionSetup:
    return instruction_setup.single_instruction_setup_for_parser(instruction_name,
                                                                 Parser())


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationSectionInstruction:
        py_source_file_name = rest_of_line.strip()

        if not py_source_file_name or py_source_file_name.isspace():
            raise SingleInstructionInvalidArgumentException('Missing python source file argument')

        return Instruction(py_source_file_name)


class Instruction(ConfigurationSectionInstruction):
    def __init__(self, py_source_file_name: str):
        self.py_source_file_name = py_source_file_name

    def execute(self,
                environment: ConfigurationSectionEnvironment):
        pre_processor = PreprocessorViaExternalProgram([
            sys.executable,
            self.py_source_file_name
        ])

        environment.preprocessor = pre_processor
