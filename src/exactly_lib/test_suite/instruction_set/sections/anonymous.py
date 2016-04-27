import shlex

from exactly_lib.default.program_modes.test_case import instruction_name_and_argument_splitter
from exactly_lib.document import parse
from exactly_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SectionElementParserForDictionaryOfInstructions, SingleInstructionParser, SingleInstructionInvalidArgumentException, \
    SingleInstructionParserSource
from exactly_lib.test_case.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.test_case.test_case_processing import Preprocessor
from exactly_lib.test_suite.instruction_set.instruction import TestSuiteInstruction


def new_parser() -> parse.SectionElementParser:
    return SectionElementParserForDictionaryOfInstructions(
        instruction_name_and_argument_splitter.splitter,
        {
            'preprocessor': PreprocessorInstructionParser()
        }
    )


class AnonymousSectionEnvironment:
    def __init__(self,
                 initial_preprocessor: Preprocessor):
        self._preprocessor = initial_preprocessor

    @property
    def preprocessor(self) -> Preprocessor:
        return self._preprocessor

    @preprocessor.setter
    def preprocessor(self, value: Preprocessor):
        self._preprocessor = value


class AnonymousSectionInstruction(TestSuiteInstruction):
    def execute(self,
                environment: AnonymousSectionEnvironment):
        """
        Updates the environment.
        """
        raise NotImplementedError()


class PreprocessorInstructionParser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AnonymousSectionInstruction:
        arg = source.instruction_argument.strip()
        if arg == '':
            raise SingleInstructionInvalidArgumentException('A preprocessor program must be given.')
        return PreprocessorInstruction(shlex.split(arg))


class PreprocessorInstruction(AnonymousSectionInstruction):
    def __init__(self,
                 command_and_arguments: list):
        self.command_and_arguments = command_and_arguments

    def execute(self,
                environment: AnonymousSectionEnvironment):
        """
        Updates the environment.
        """
        environment.preprocessor = PreprocessorViaExternalProgram(self.command_and_arguments)
