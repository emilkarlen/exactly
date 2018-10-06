from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.entity import conf_params
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.help.entities.configuration_parameters.objects.timeout import WHAT_THE_TIMEOUT_APPLIES_TO
from exactly_lib.instructions.configuration.utils.single_arg_utils import single_eq_invokation_variants, \
    extract_single_eq_argument_string
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import sh
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    _INTEGER_ARG_NAME = a.Named('INTEGER')

    def __init__(self, name: str):
        super().__init__(name, {
            'default_value_str': conf_params.TIMEOUT_CONF_PARAM_INFO.default_value_single_line_description,
            'phase': PHASE_NAME_DICTIONARY,
        })

    def single_line_description(self) -> str:
        return self._tp.format(_SINGLE_LINE_DESCRIPTION)

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> List[InvokationVariant]:
        return single_eq_invokation_variants(self._INTEGER_ARG_NAME)

    def syntax_element_descriptions(self) -> List[ParagraphItem]:
        return [
            SyntaxElementDescription(self._INTEGER_ARG_NAME.name,
                                     self._tp.fnap('Timeout in seconds.'))
        ]

    def see_also_targets(self) -> list:
        return [conf_params.TIMEOUT_CONF_PARAM_INFO.cross_reference_target]


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationPhaseInstruction:
        argument = extract_single_eq_argument_string(rest_of_line)
        try:
            value = int(argument)
        except ValueError:
            raise SingleInstructionInvalidArgumentException('Not an integer: `%s`' % argument)
        if value < 0:
            raise SingleInstructionInvalidArgumentException('Timeout cannot be negative: `%s`' % argument)
        return _Instruction(value)


class _Instruction(ConfigurationPhaseInstruction):
    def __init__(self,
                 timeout: int):
        self.timeout = timeout

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_timeout_in_seconds(self.timeout)
        return sh.new_sh_success()


_SINGLE_LINE_DESCRIPTION = """\
Sets the timeout of sub processes executed by instructions and the {phase[act]} phase."""

_MAIN_DESCRIPTION_REST = """\
Default: {default_value_str}


""" + WHAT_THE_TIMEOUT_APPLIES_TO
