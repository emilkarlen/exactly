from exactly_lib.default.program_modes.test_case.default_instruction_names import TIMEOUT_INSTRUCTION_NAME
from exactly_lib.help.concepts.contents_structure import ConfigurationParameterDocumentation, Name
from exactly_lib.help.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help.utils.phase_names import phase_name_dictionary, CONFIGURATION_PHASE_NAME
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure.structures import text


class _TimeoutConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(Name('timeout', 'timeouts'))

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(text(_SINGLE_LINE_DESCRIPTION.format(phase=phase_name_dictionary())),
                        []))

    def default_value_str(self) -> str:
        return 'No timeout.'

    def see_also(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   TIMEOUT_INSTRUCTION_NAME),
        ]


TIMEOUT_CONFIGURATION_PARAMETER = _TimeoutConfigurationParameter()

_SINGLE_LINE_DESCRIPTION = """\
Timeout of the {phase[act]} phase, in seconds."""
