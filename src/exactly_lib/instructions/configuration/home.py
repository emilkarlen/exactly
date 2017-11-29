import pathlib

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import conf_params, concepts
from exactly_lib.help_texts.name_and_cross_ref import cross_reference_id_list
from exactly_lib.instructions.utils.documentation import documentation_text
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.misc_utils import split_arguments_list_string
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'home_directory': formatting.conf_param_(conf_params.HOME_CASE_DIRECTORY_CONF_PARAM_INFO),
            'PATH': _ARG_NAME
        })

    def single_line_description(self) -> str:
        return self._format('Sets the {home_directory} directory')

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

    def see_also_targets(self) -> list:
        return cross_reference_id_list([
            conf_params.HOME_CASE_DIRECTORY_CONF_PARAM_INFO,
            concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO,
        ])


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
        new_path = self._new_path(configuration_builder)
        if not new_path.exists():
            return sh.new_sh_hard_error('Directory does not exist: {}'.format(new_path))
        if not new_path.is_dir():
            return sh.new_sh_hard_error('Not a directory: {}'.format(new_path))
        configuration_builder.set_home_case_dir(new_path.resolve())
        return sh.new_sh_success()

    def _new_path(self,
                  configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        delta = pathlib.Path(self.argument)
        if delta.is_absolute():
            return delta
        return configuration_builder.home_case_dir_path / delta
