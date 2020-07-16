import functools
import pathlib
import unittest
from typing import Dict, List

from exactly_lib.execution.phase_file_space import PhaseTmpFileSpaceFactory
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phase_identifier import PhaseEnum, Phase
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.partial_execution.test_resources.basic import test, \
    Result
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, \
    cleanup_phase_instruction_that, act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions


def suite() -> unittest.makeSuite:
    return unittest.makeSuite(TestInstructionTmpDirs)


class TestInstructionTmpDirs(unittest.TestCase):
    def test_instruction_environment_specifies_correct_tmp_dir_space_for_each_instruction(self):
        # ARRANGE #
        recorder = {}

        setup_phase_instr_that_records = setup_phase_instruction_that(
            validate_post_setup_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.SETUP, recorder),
            main_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.SETUP, recorder),
        )
        before_assert_phase_instr_that_records = before_assert_phase_instruction_that(
            validate_post_setup_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.BEFORE_ASSERT, recorder),
            main_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.BEFORE_ASSERT, recorder)
        )
        assert_phase_instr_that_records = assert_phase_instruction_that(
            validate_post_setup_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.ASSERT, recorder),
            main_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.ASSERT, recorder)
        )
        cleanup_phase_instr_that_records = cleanup_phase_instruction_that(
            main_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.CLEANUP, recorder)
        )
        test_case = partial_test_case_with_instructions(
            [
                setup_phase_instr_that_records,
                setup_phase_instr_that_records,
            ],
            [act_phase_instruction_with_source(LineSequence(1, ('line',)))],
            [
                before_assert_phase_instr_that_records,
                before_assert_phase_instr_that_records,
            ],
            [
                assert_phase_instr_that_records,
                assert_phase_instr_that_records,
            ],
            [
                cleanup_phase_instr_that_records,
                cleanup_phase_instr_that_records,
            ],
        )
        actor_that_registers_tmp_dirs = ActorThatRunsConstantActions(
            validate_post_setup_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.ACT, recorder),
            prepare_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.ACT, recorder),
            execute_initial_action=RecordTmpDirForInstructionInPhase(PhaseEnum.ACT, recorder),
        )
        # ACT & ASSERT #
        test(
            self,
            test_case,
            actor_that_registers_tmp_dirs,
            functools.partial(tmp_dir_is_correct_for_each_instruction, recorder, 2),
            is_keep_sandbox=False)


def tmp_dir_is_correct_for_each_instruction(recordings: Dict[PhaseEnum, List[pathlib.Path]],
                                            num_instructions_per_phase: int,
                                            put: unittest.TestCase,
                                            actual: Result):
    sds = actual.sds

    def dirs_for_validation(phase: Phase) -> List[pathlib.Path]:
        file_space_factory = PhaseTmpFileSpaceFactory(sds.internal_tmp_dir)
        return [
            file_space_factory.instruction__validation(phase, n).root_dir__may_not_exist
            for n in range(1, num_instructions_per_phase + 1)
        ]

    def dirs_for_main(phase: Phase) -> List[pathlib.Path]:
        file_space_factory = PhaseTmpFileSpaceFactory(sds.internal_tmp_dir)
        return [
            file_space_factory.instruction__main(phase, n).root_dir__may_not_exist
            for n in range(1, num_instructions_per_phase + 1)
        ]

    def dirs_for_act() -> List[pathlib.Path]:
        space_factory__v = PhaseTmpFileSpaceFactory(sds.internal_tmp_dir)
        space_factory__m = PhaseTmpFileSpaceFactory(sds.internal_tmp_dir)

        return [
            space_factory__v.for_phase__validation(phase_identifier.ACT).root_dir__may_not_exist,
            space_factory__m.for_phase__main(phase_identifier.ACT).root_dir__may_not_exist,
            space_factory__m.for_phase__main(phase_identifier.ACT).root_dir__may_not_exist,
        ]

    put.assertFalse(actual.partial_result.is_failure)

    expected = {
        PhaseEnum.SETUP:
            dirs_for_main(phase_identifier.SETUP) + dirs_for_validation(phase_identifier.SETUP),

        PhaseEnum.ACT:
            dirs_for_act(),

        PhaseEnum.BEFORE_ASSERT:
            dirs_for_validation(phase_identifier.BEFORE_ASSERT) + dirs_for_main(phase_identifier.BEFORE_ASSERT),

        PhaseEnum.ASSERT:
            dirs_for_validation(phase_identifier.ASSERT) + dirs_for_main(phase_identifier.ASSERT),

        PhaseEnum.CLEANUP:
            dirs_for_main(phase_identifier.CLEANUP),
    }
    put.assertDictEqual(expected,
                        recordings,
                        'Tmp directory per phase')


class RecordTmpDirForInstructionInPhase:
    def __init__(self, phase: PhaseEnum, recorder: Dict[PhaseEnum, List[pathlib.Path]]):
        self.phase = phase
        self.recorder = recorder

    def __call__(self, environment: InstructionEnvironmentForPostSdsStep, *args):
        next_path_in_instruction_dir = environment.tmp_dir__path_access.root_dir__may_not_exist

        value_for_phase = self.recorder.setdefault(self.phase, [])
        value_for_phase.append(next_path_in_instruction_dir)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
