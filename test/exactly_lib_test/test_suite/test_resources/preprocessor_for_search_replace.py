import pathlib
import shlex

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib_test.common.test_resources import instruction_setup
from exactly_lib_test.test_suite.test_resources.instructions import configuration_section_instruction_that


def setup(instruction_name: str) -> SingleInstructionSetup:
    return instruction_setup.single_instruction_setup_for_parser(instruction_name,
                                                                 Parser())


class Parser(InstructionParserThatConsumesCurrentLine):
    """
    Syntax: FROM TO
    """

    def _parse(self, rest_of_line: str) -> ConfigurationSectionInstruction:
        arguments = shlex.split(rest_of_line)

        if len(arguments) != 2:
            raise SingleInstructionInvalidArgumentException('Invalid syntax: expected: FROM TO')

        def set_preprocessor(conf: ConfigurationSectionEnvironment):
            preproc = SearchReplacePreprocessor(arguments[0],
                                                arguments[1])
            conf.preprocessor = preproc

        return configuration_section_instruction_that(set_preprocessor)


class SearchReplacePreprocessor(Preprocessor):
    def __init__(self,
                 to_replace: str,
                 replacement: str
                 ):
        self.to_replace = to_replace
        self.replacement = replacement

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        return test_case_source.replace(self.to_replace,
                                        self.replacement)
