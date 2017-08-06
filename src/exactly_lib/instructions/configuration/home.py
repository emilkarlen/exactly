import pathlib

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.configuration_parameters.home_case_directory import \
    HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help_texts.names import formatting
from exactly_lib.instructions.utils.documentation import documentation_text
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case_utils.parse.misc_utils import split_arguments_list_string


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'home_directory': formatting.concept(HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'PATH': _ARG_NAME
        })

    def single_line_description(self) -> str:
        return self._format('Sets the {home_directory}')

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(_ARG_NAME, []),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(_ARG_NAME,
                                     self._paragraphs(_PATH_DESCRIPTION) +
                                     documentation_text.paths_uses_posix_syntax()),
        ]

    def _see_also_cross_refs(self) -> list:
        return [HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target()]


_ARG_NAME = 'PATH'

_PATH_DESCRIPTION = """\
An absolute or relative name of an existing directory.


If {PATH} is relative, then it's relative to the current {home_directory}.
"""


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationPhaseInstruction:
        arguments = split_arguments_list_string(rest_of_line)
        if len(arguments) != 1:
            msg = 'Invalid number of arguments (exactly one expected), found {}'.format(str(len(arguments)))
            raise SingleInstructionInvalidArgumentException(msg)
        return _Instruction(arguments[0])


class _Instruction(ConfigurationPhaseInstruction):
    def __init__(self,
                 argument: str):
        self.argument = argument

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        new_home_dir_path = self._new_home(configuration_builder)
        if not new_home_dir_path.exists():
            return sh.new_sh_hard_error('Directory does not exist: {}'.format(new_home_dir_path))
        if not new_home_dir_path.is_dir():
            return sh.new_sh_hard_error('Not a directory: {}'.format(new_home_dir_path))
        configuration_builder.set_home_case_dir(new_home_dir_path.resolve())
        return sh.new_sh_success()

    def _new_home(self,
                  configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        delta = pathlib.Path(self.argument)
        if delta.is_absolute():
            return delta
        return configuration_builder.home_case_dir_path / delta
