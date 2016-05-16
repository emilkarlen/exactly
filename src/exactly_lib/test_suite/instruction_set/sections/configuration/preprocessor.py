import shlex

from exactly_lib.common.instruction_documentation import InstructionDocumentation, InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.plain_concepts.preprocessor import PREPROCESSOR_CONCEPT
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib.util.textformat.structure.structures import paras


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(_InstructionParser(),
                                  _TheInstructionDocumentation(instruction_name))


class _TheInstructionDocumentation(InstructionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Sets a preprocessor to use for each test case in the suite'

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                'EXECUTABLE [ARGUMENT...]',
                paras('An executable program that will be given the test case file as single argument')),
        ]

    def see_also(self) -> list:
        return [
            PREPROCESSOR_CONCEPT.cross_reference_target(),
        ]


class _InstructionParser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> ConfigurationSectionInstruction:
        arg = source.instruction_argument.strip()
        if arg == '':
            raise SingleInstructionInvalidArgumentException('A preprocessor program must be given.')
        return _Instruction(shlex.split(arg))


class _Instruction(ConfigurationSectionInstruction):
    def __init__(self,
                 command_and_arguments: list):
        self.command_and_arguments = command_and_arguments

    def execute(self,
                environment: ConfigurationSectionEnvironment):
        """
        Updates the environment.
        """
        environment.preprocessor = PreprocessorViaExternalProgram(self.command_and_arguments)
