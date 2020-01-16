from typing import List

from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts, conf_params
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions.instruction_names import TEST_CASE_STATUS_INSTRUCTION_NAME
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_for_configuration_phase
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.test_case.test_case_status import NAME_SKIP
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class ConfigurationPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)

        self._parser = TextParser({
            'configuration_parameters': formatting.concept(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.plural_name),
            'execution_mode': formatting.conf_param_(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO),
            'SKIP': NAME_SKIP,
            'setup': phase_names.SETUP,
        })

    def purpose(self) -> Description:
        first_line = self._parser.text(ONE_LINE_DESCRIPTION)
        remaining_lines = []
        return Description(first_line, remaining_lines)

    def sequence_info(self) -> PhaseSequenceInfo:
        preceding_phase = self._parser.fnap(SEQUENCE_INFO__PRECEDING_PHASE)
        succeeding_phase = self._parser.fnap(SEQUENCE_INFO__SUCCEEDING_PHASE)
        return PhaseSequenceInfo(preceding_phase, succeeding_phase)

    def instruction_purpose_description(self) -> List[ParagraphItem]:
        return self._parser.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(cwd_at_start_of_phase_for_configuration_phase())

    @property
    def _see_also_targets_specific(self) -> List[SeeAlsoTarget]:
        return [
            concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.cross_reference_target,
            conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.cross_reference_target,
            self.section_info.instruction_cross_reference_target(TEST_CASE_STATUS_INSTRUCTION_NAME),
            phase_infos.SETUP.cross_reference_target,
        ]


ONE_LINE_DESCRIPTION = """\
Configures the execution of the remaining phases by setting {configuration_parameters}."""

INSTRUCTION_PURPOSE_DESCRIPTION = 'Each instruction sets one of the {configuration_parameters}.'

SEQUENCE_INFO__PRECEDING_PHASE = 'This is the first phase.'

SEQUENCE_INFO__SUCCEEDING_PHASE = """\
If the {execution_mode} is set to {SKIP}, then the remaining phases are not executed.

Otherwise, the {setup} phase follows.
"""
