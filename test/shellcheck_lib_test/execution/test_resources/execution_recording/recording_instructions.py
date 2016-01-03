from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction
from shellcheck_lib_test.execution.test_resources.execution_recording.recorder import ListElementRecorder, ListRecorder
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import cleanup_phase_instruction_that, \
    assert_phase_instruction_that, setup_phase_instruction_that, anonymous_phase_instruction_that, \
    act_phase_instruction_that, before_assert_phase_instruction_that


class RecordingInstructions:
    def __init__(self, recorder: ListRecorder):
        self.recorder = recorder

    def new_anonymous_instruction(self, value) -> AnonymousPhaseInstruction:
        return anonymous_phase_instruction_that(main=self._do_record_and_return_sh(value))

    def new_setup_instruction(self,
                              value_for_validate_pre_eds,
                              value_for_main,
                              value_for_validate_post_eds) -> SetupPhaseInstruction:
        return setup_phase_instruction_that(validate_pre_eds=self._do_record_and_return_svh(value_for_validate_pre_eds),
                                            validate_post_eds=self._do_record_and_return_svh(
                                                    value_for_validate_post_eds),
                                            main=self._do_record_and_return_sh(value_for_main))

    def new_act_instruction(self,
                            value_for_validate_pre_eds,
                            value_for_validate_post_eds,
                            value_for_main) -> ActPhaseInstruction:
        return act_phase_instruction_that(validate_pre_eds=self._do_record_and_return_svh(value_for_validate_pre_eds),
                                          validate_post_eds=self._do_record_and_return_svh(value_for_validate_post_eds),
                                          main=self._do_record_and_return_sh(value_for_main))

    def new_before_assert_instruction(self,
                                      value_for_validate_pre_eds,
                                      value_for_main,
                                      value_for_validate_post_eds) -> BeforeAssertPhaseInstruction:
        return before_assert_phase_instruction_that(
                validate_pre_eds=self._do_record_and_return_svh(value_for_validate_pre_eds),
                validate_post_eds=self._do_record_and_return_svh(value_for_validate_post_eds),
                main=self._do_record_and_return_sh(value_for_main))

    def new_assert_instruction(self,
                               value_for_validate_pre_eds,
                               value_for_validate,
                               value_for_execute) -> AssertPhaseInstruction:
        return assert_phase_instruction_that(
                validate_pre_eds=self._do_record_and_return_svh(value_for_validate_pre_eds),
                validate_post_eds=self._do_record_and_return_svh(value_for_validate),
                main=self._do_record_and_return(value_for_execute,
                                                pfh.new_pfh_pass()))

    def new_cleanup_instruction(self,
                                value_for_validate_pre_eds,
                                value_for_main) -> CleanupPhaseInstruction:
        return cleanup_phase_instruction_that(
                validate_pre_eds=self._do_record_and_return_svh(value_for_validate_pre_eds),
                main=self._do_record_and_return_sh(value_for_main))

    def __recorder_of(self, element) -> ListElementRecorder:
        return self.recorder.recording_of(element)

    def _do_record_and_return_sh(self, element):
        return self._do_record_and_return(element,
                                          sh.new_sh_success())

    def _do_record_and_return_svh(self, element):
        return self._do_record_and_return(element,
                                          svh.new_svh_success())

    def _do_record_and_return(self, element, return_value):
        def ret_val():
            self.recorder.recording_of(element).record()
            return return_value

        return ret_val
