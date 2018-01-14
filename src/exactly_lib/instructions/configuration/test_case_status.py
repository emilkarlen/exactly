from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import conf_params, concepts
from exactly_lib.instructions.configuration.utils.single_arg_utils import single_eq_invokation_variants, \
    extract_single_eq_argument_string
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.test_case_status import ExecutionMode, NAME_2_STATUS
from exactly_lib.util.cli_syntax.elements import argument as a


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'status_config_param': formatting.conf_param(
                conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.informative_name),
            'conf_param': concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.singular_name,
            'default_mode': conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.default_value_single_line_description,
        })

    def single_line_description(self) -> str:
        return self._format('Sets the {status_config_param} {conf_param}')

    def main_description_rest(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> list:
        return single_eq_invokation_variants(a.Named(_ARG_NAME))

    def syntax_element_descriptions(self) -> list:
        from exactly_lib.help.entities.configuration_parameters.objects.test_case_status import \
            execution_modes_list
        return [
            SyntaxElementDescription(_ARG_NAME,
                                     [execution_modes_list()])
        ]

    def see_also_targets(self) -> list:
        return [conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.cross_reference_target]


_ARG_NAME = formatting.syntax_element(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.configuration_parameter_name)


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationPhaseInstruction:
        status_element_arg = extract_single_eq_argument_string(rest_of_line)
        argument = status_element_arg.upper()
        try:
            target = NAME_2_STATUS[argument]
        except KeyError:
            raise SingleInstructionInvalidArgumentException('Invalid {status}: `{actual}`'.format(
                status=conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.configuration_parameter_name,
                actual=status_element_arg))
        return _Instruction(target)


class _Instruction(ConfigurationPhaseInstruction):
    def __init__(self,
                 mode_to_set: ExecutionMode):
        self.mode_to_set = mode_to_set

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.mode_to_set)
        return sh.new_sh_success()


_MAIN_DESCRIPTION_REST = """\
The default {status_config_param} (if not changed by this instruction) is {default_mode}.
"""
