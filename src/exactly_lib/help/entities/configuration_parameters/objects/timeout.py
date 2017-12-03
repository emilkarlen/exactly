from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.entity.conf_params import TIMEOUT_CONF_PARAM_INFO
from exactly_lib.help_texts.test_case.instructions.instruction_names import TIMEOUT_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, \
    PHASE_NAME_DICTIONARY
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser


class _TimeoutConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(TIMEOUT_CONF_PARAM_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        parse = TextParser({
            'phase': PHASE_NAME_DICTIONARY,
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        parse.fnap(WHAT_THE_TIMEOUT_APPLIES_TO)))

    def see_also_targets(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   TIMEOUT_INSTRUCTION_NAME),
        ]


DOCUMENTATION = _TimeoutConfigurationParameter()

WHAT_THE_TIMEOUT_APPLIES_TO = """\
The timeout is per instruction, and for the {phase[act]} phase.
It does not apply to the test case as a whole.
"""
