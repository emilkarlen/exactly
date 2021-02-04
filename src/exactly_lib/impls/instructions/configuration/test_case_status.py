from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import conf_params, concepts
from exactly_lib.impls.instructions.configuration.utils.single_arg_utils import single_eq_invokation_variants, \
    extract_single_eq_argument_string
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import svh
from exactly_lib.test_case.test_case_status import TestCaseStatus, NAME_2_STATUS
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.document import SectionContents


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
        return self._tp.format('Sets the {status_config_param} {conf_param}')

    def invokation_variants(self) -> List[InvokationVariant]:
        return single_eq_invokation_variants(a.Named(_ARG_NAME))

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        from exactly_lib.help.entities.configuration_parameters.objects.test_case_status import \
            execution_modes_list
        return [
            SyntaxElementDescription(_ARG_NAME,
                                     [execution_modes_list()])
        ]

    def notes(self) -> SectionContents:
        return self._tp.section_contents(_NOTES)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.cross_reference_target]


_ARG_NAME = formatting.syntax_element(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.configuration_parameter_name)


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationPhaseInstruction:
        status_element_arg = extract_single_eq_argument_string(_ARG_NAME, rest_of_line)
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
                 mode_to_set: TestCaseStatus):
        self.mode_to_set = mode_to_set

    def main(self, configuration_builder: ConfigurationBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        configuration_builder.set_test_case_status(self.mode_to_set)
        return svh.new_svh_success()


_NOTES = """\
The default {status_config_param} is {default_mode}.
"""
