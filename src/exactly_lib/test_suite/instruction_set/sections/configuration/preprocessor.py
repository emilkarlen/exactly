from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.configuration.utils.single_arg_utils import MANDATORY_EQ_ARG, \
    extract_mandatory_arguments_after_eq
from exactly_lib.processing.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'preprocessor': formatting.concept_(concepts.PREPROCESSOR_CONCEPT_INFO),
            'shell_cmd_line': syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT.singular_name,
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
        })

    def single_line_description(self) -> str:
        return self._tp.format('Sets a {preprocessor} to transform each test case file in the suite')

    def invokation_variants(self) -> List[InvokationVariant]:
        shell_cmd_arg = a.Single(a.Multiplicity.MANDATORY,
                                 syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT.argument)
        return [
            invokation_variant_from_args([MANDATORY_EQ_ARG,
                                          shell_cmd_arg]),
        ]

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_DESCRIPTION)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            concepts.PREPROCESSOR_CONCEPT_INFO.cross_reference_target,
            syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT.cross_reference_target,
            concepts.SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target,
        ]


_DESCRIPTION = """\
The {preprocessor} is only used for the test cases in the current suite -
not in sub suites.


{shell_cmd_line} uses {shell_syntax_concept}.
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
