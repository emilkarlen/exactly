import shlex

from exactly_lib.common.instruction_documentation import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.plain_concepts.preprocessor import PREPROCESSOR_CONCEPT
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib.util.cli_syntax.elements import argument as a


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(_InstructionParser(),
                                  _TheInstructionDocumentation(instruction_name))


class _TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {})
        self.executable = a.Named('EXECUTABLE')

    def single_line_description(self) -> str:
        return 'Sets a preprocessor to use for each test case in the suite'

    def invokation_variants(self) -> list:
        executable_arg = a.Single(a.Multiplicity.MANDATORY,
                                  self.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                          a.Named('ARGUMENT'))
        return [
            InvokationVariant(self._cl_syntax_for_args([executable_arg,
                                                        optional_arguments_arg])),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.executable.name,
                                     self._paragraphs('The path of an existing executable file.'))
        ]

    def main_description_rest(self) -> list:
        return self._paragraphs(_DESCRIPTION)

    def see_also(self) -> list:
        return [
            PREPROCESSOR_CONCEPT.cross_reference_target(),
        ]


_DESCRIPTION = """\
An executable program that will be given the test case file as single (additional) argument.


The command line uses shell syntax.
"""


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
