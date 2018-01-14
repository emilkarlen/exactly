from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import concepts
from exactly_lib.instructions.configuration.utils.single_arg_utils import MANDATORY_EQ_ARG, \
    extract_mandatory_arguments_after_eq
from exactly_lib.processing.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib.util.cli_syntax.elements import argument as a


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.executable = a.Named('EXECUTABLE')
        self.argument = a.Named('ARGUMENT')
        super().__init__(name, {
            'EXECUTABLE': self.executable.name,
            'ARGUMENT': self.argument.name,
            'preprocessor': formatting.concept_(concepts.PREPROCESSOR_CONCEPT_INFO),
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
        })

    def single_line_description(self) -> str:
        return self._format('Sets a {preprocessor} to use for each test case in the suite')

    def invokation_variants(self) -> list:
        executable_arg = a.Single(a.Multiplicity.MANDATORY,
                                  self.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                          self.argument)
        return [
            InvokationVariant(self._cl_syntax_for_args([MANDATORY_EQ_ARG,
                                                        executable_arg,
                                                        optional_arguments_arg])),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.executable.name,
                                     self._paragraphs('The path of an existing executable file.'))
        ]

    def main_description_rest(self) -> list:
        return self._paragraphs(_DESCRIPTION)

    def see_also_targets(self) -> list:
        return [
            concepts.PREPROCESSOR_CONCEPT_INFO.cross_reference_target,
            concepts.SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target,
        ]


_DESCRIPTION = """\
The program will be given the test case file as single (additional) argument.


The {preprocessor} is only used for the test cases in the current suite -
not in sub suites.


{EXECUTABLE} and {ARGUMENT} uses {shell_syntax_concept}.
"""


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationSectionInstruction:
        command_and_arguments = extract_mandatory_arguments_after_eq(rest_of_line)
        return Instruction(command_and_arguments)


class Instruction(ConfigurationSectionInstruction):
    def __init__(self,
                 command_and_arguments: list):
        self.command_and_arguments = command_and_arguments

    def execute(self,
                environment: ConfigurationSectionEnvironment):
        """
        Updates the environment.
        """
        environment.preprocessor = PreprocessorViaExternalProgram(self.command_and_arguments)
