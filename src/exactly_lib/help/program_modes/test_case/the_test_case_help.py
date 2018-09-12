from typing import Sequence, Dict

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.file_inclusion_directive import FileInclusionDirectiveDocumentation
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation, SectionInstructionSet
from exactly_lib.help.program_modes.test_case.config import phase_help_name
from exactly_lib.help.program_modes.test_case.contents.phase import configuration, setup, act, before_assert, assert_, \
    cleanup
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.test_case import phase_identifier


def test_case_help(instructions_setup: InstructionsSetup) -> TestCaseHelp:
    return TestCaseHelp(phase_helps_for(instructions_setup))


def phase_helps_for(instructions_setup: InstructionsSetup) -> Sequence[SectionDocumentation]:
    return [
        configuration.ConfigurationPhaseDocumentation(
            phase_help_name(phase_identifier.CONFIGURATION),
            _phase_instruction_set_help(instructions_setup.config_instruction_set)),

        setup.SetupPhaseDocumentation(
            phase_help_name(phase_identifier.SETUP),
            _phase_instruction_set_help(instructions_setup.setup_instruction_set)),

        act.ActPhaseDocumentation(phase_help_name(phase_identifier.ACT)),

        before_assert.BeforeAssertPhaseDocumentation(
            phase_help_name(phase_identifier.BEFORE_ASSERT),
            _phase_instruction_set_help(instructions_setup.before_assert_instruction_set)),

        assert_.AssertPhaseDocumentation(
            phase_help_name(phase_identifier.ASSERT),
            _phase_instruction_set_help(instructions_setup.assert_instruction_set)),

        cleanup.CleanupPhaseDocumentation(
            phase_help_name(phase_identifier.CLEANUP),
            _phase_instruction_set_help(instructions_setup.cleanup_instruction_set)),
    ]


def _phase_instruction_set_help(single_instruction_setup_dic: Dict[str, SingleInstructionSetup]
                                ) -> SectionInstructionSet:
    return SectionInstructionSet(
        list(map(lambda x: x.documentation, single_instruction_setup_dic.values())) +
        [FileInclusionDirectiveDocumentation()]
    )
