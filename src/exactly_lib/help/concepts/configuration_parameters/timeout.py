from exactly_lib.default.program_modes.test_case.default_instruction_names import TIMEOUT_INSTRUCTION_NAME
from exactly_lib.help.concepts.contents_structure import ConfigurationParameterDocumentation, Name
from exactly_lib.help.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help.utils.phase_names import phase_name_dictionary, CONFIGURATION_PHASE_NAME
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description


class _TimeoutConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(Name('timeout', 'timeouts'))

    def purpose(self) -> DescriptionWithSubSections:
        parse = TextParser({
            'phase': phase_name_dictionary(),
        })
        return from_simple_description(
            Description(parse.text(_SINGLE_LINE_DESCRIPTION),
                        parse.fnap(WHAT_THE_TIMEOUT_APPLIES_TO)))

    def default_value_str(self) -> str:
        return 'No timeout.'

    def see_also(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   TIMEOUT_INSTRUCTION_NAME),
        ]


TIMEOUT_CONFIGURATION_PARAMETER = _TimeoutConfigurationParameter()

_SINGLE_LINE_DESCRIPTION = """\
Timeout of sub processes executed by instructions and the {phase[act]} phase."""

WHAT_THE_TIMEOUT_APPLIES_TO = """\
The timeout is per instruction, and for the {phase[act]} phase.
It does not apply to the whole test case.
"""
