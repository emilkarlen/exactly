import functools
import types

from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from shellcheck_lib_test.execution.test_resources import instruction_that_do_and_return


class Recorder:
    def __init__(self):
        self.phaseStep2recording = dict()
        self.list_recorder = []

    def set_phase_step_recording(self,
                                 phase_step: PhaseStep,
                                 recording):
        self.phaseStep2recording[phase_step] = recording

    def recording_for_phase(self,
                            phase_step: PhaseStep):
        return self.phaseStep2recording[phase_step]

    def add_list_recording(self,
                           recording):
        self.list_recorder.append(recording)

    def add_list_recordings(self,
                            recordings: list):
        self.list_recorder.extend(recordings)


def do_nothing(recorder: Recorder, *args):
    pass


class TestCaseSetupWithRecorder(tuple):
    def __new__(cls,
                ret_val_from_validate: svh.SuccessOrValidationErrorOrHardError = svh.new_svh_success(),
                ret_val_from_execute: sh.SuccessOrHardError = sh.new_sh_success(),
                ret_val_from_assert_execute: pfh.PassOrFailOrHardError = pfh.new_pfh_pass(),
                validation_action__without_eds: types.FunctionType = do_nothing,
                anonymous_phase_action: types.FunctionType = do_nothing,
                validation_action__with_eds: types.FunctionType = do_nothing,
                execution_action__with_eds: types.FunctionType = do_nothing,
                execution__generate_script: types.FunctionType =
                instruction_that_do_and_return.do_nothing__generate_script,
                ):
        return tuple.__new__(cls, (ret_val_from_validate,
                                   ret_val_from_execute,
                                   ret_val_from_assert_execute,
                                   validation_action__without_eds,
                                   anonymous_phase_action,
                                   validation_action__with_eds,
                                   execution_action__with_eds,
                                   execution__generate_script,
                                   ))

    def as_plain_test_case_setup(self,
                                 recorder: Recorder) -> instruction_that_do_and_return.TestCaseSetup:
        return instruction_that_do_and_return.TestCaseSetup(
                ret_val_from_validate=self.ret_val_from_validate,
                ret_val_from_main=self.ret_val_from_main,
                ret_val_from_assert_main=self.ret_val_from_assert_main,
                validation_action__pre_eds=functools.partial(self.validation_action__pre_eds,
                                                             recorder),
                anonymous_phase_action=functools.partial(self.anonymous_phase_action,
                                                         recorder),
                validation_action__post_eds=functools.partial(self.validation_action__post_eds,
                                                              recorder),
                main_action__post_eds=functools.partial(self.main_action__post_eds,
                                                        recorder),
                main__generate_script=self.main__generate_script)

    @property
    def ret_val_from_validate(self) -> svh.SuccessOrValidationErrorOrHardError:
        return self[0]

    @property
    def ret_val_from_main(self) -> sh.SuccessOrHardError:
        return self[1]

    @property
    def ret_val_from_assert_main(self) -> pfh.PassOrFailOrHardError:
        return self[2]

    @property
    def validation_action__pre_eds(self) -> types.FunctionType:
        return self[3]

    @property
    def anonymous_phase_action(self) -> types.FunctionType:
        return self[4]

    @property
    def validation_action__post_eds(self) -> types.FunctionType:
        return self[5]

    @property
    def main_action__post_eds(self) -> types.FunctionType:
        return self[6]

    @property
    def main__generate_script(self) -> types.FunctionType:
        return self[7]


def new_recording_test_case(
        setup_with_recorder: TestCaseSetupWithRecorder,
        recorder: Recorder) -> test_case_doc.TestCase:
    return instruction_that_do_and_return.TestCaseGeneratorForTestCaseSetup(
            setup_with_recorder.as_plain_test_case_setup(recorder)).test_case
