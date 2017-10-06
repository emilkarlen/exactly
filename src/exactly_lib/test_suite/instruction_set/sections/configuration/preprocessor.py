import shlex

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.entities.concepts.plain_concepts.preprocessor import PREPROCESSOR_CONCEPT
from exactly_lib.help.entities.concepts.plain_concepts.shell_syntax import SHELL_SYNTAX_CONCEPT
from exactly_lib.help_texts.names import formatting
from exactly_lib.processing.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
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
            'preprocessor': formatting.concept(PREPROCESSOR_CONCEPT.singular_name()),
            'shell_syntax_concept': formatting.concept(SHELL_SYNTAX_CONCEPT.singular_name()),
        })

    def single_line_description(self) -> str:
        return self._format('Sets a {preprocessor} to use for each test case in the suite')

    def invokation_variants(self) -> list:
        executable_arg = a.Single(a.Multiplicity.MANDATORY,
                                  self.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                          self.argument)
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

    def see_also_targets(self) -> list:
        from exactly_lib.help.utils.entity_documentation import cross_reference_id_list
        return cross_reference_id_list([
            PREPROCESSOR_CONCEPT,
            SHELL_SYNTAX_CONCEPT,
        ])


_DESCRIPTION = """\
The program will be given the test case file as single (additional) argument.


The {preprocessor} is only used for the test cases in the current suite -
not in sub suites.


{EXECUTABLE} and {ARGUMENT} uses {shell_syntax_concept}.
"""


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationSectionInstruction:
        arg = rest_of_line.strip()
        if arg == '':
            raise SingleInstructionInvalidArgumentException('A preprocessor program must be given.')
        try:
            command_and_arguments = shlex.split(arg)
        except:
            raise SingleInstructionInvalidArgumentException('Invalid quoting: ' + arg)
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
