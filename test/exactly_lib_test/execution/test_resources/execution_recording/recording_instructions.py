from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListElementRecorder, ListRecorder
from exactly_lib_test.execution.test_resources.instruction_test_resources import cleanup_phase_instruction_that, \
    assert_phase_instruction_that, setup_phase_instruction_that, configuration_phase_instruction_that, \
    before_assert_phase_instruction_that


class RecordingInstructionsFactory:
    def __init__(self, recorder: ListRecorder):
        self.recorder = recorder

    def new_configuration_instruction(self, value) -> ConfigurationPhaseInstruction:
        return configuration_phase_instruction_that(main=self._do_record_and_return_sh(value))

    def new_setup_instruction(self,
                              value_for_symbol_usages,
                              value_for_validate_pre_sds,
                              value_for_main,
                              value_for_validate_post_sds,
                              ) -> SetupPhaseInstruction:
        return setup_phase_instruction_that(
            symbol_usages_initial_action=self._do_record_first_invokation(value_for_symbol_usages),
            validate_pre_sds=self._do_record_and_return_svh(value_for_validate_pre_sds),
            validate_post_setup=self._do_record_and_return_svh(
                value_for_validate_post_sds),
            main=self._do_record_and_return_sh(value_for_main))

    def new_before_assert_instruction(self,
                                      value_for_validate_pre_sds,
                                      value_for_validate_post_sds,
                                      value_for_main) -> BeforeAssertPhaseInstruction:
        return before_assert_phase_instruction_that(
            validate_pre_sds=self._do_record_and_return_svh(value_for_validate_pre_sds),
            validate_post_setup=self._do_record_and_return_svh(value_for_validate_post_sds),
            main=self._do_record_and_return_sh(value_for_main))

    def new_assert_instruction(self,
                               value_for_validate_pre_sds,
                               value_for_validate,
                               value_for_execute) -> AssertPhaseInstruction:
        return assert_phase_instruction_that(
            validate_pre_sds=self._do_record_and_return_svh(value_for_validate_pre_sds),
            validate_post_setup=self._do_record_and_return_svh(value_for_validate),
            main=self._do_record_and_return(value_for_execute,
                                            pfh.new_pfh_pass()))

    def new_cleanup_instruction(self,
                                value_for_validate_pre_sds,
                                first_value_of_pair_for_main) -> CleanupPhaseInstruction:
        return cleanup_phase_instruction_that(
            validate_pre_sds=self._do_record_and_return_svh(value_for_validate_pre_sds),
            main=self._do_cleanup_main(first_value_of_pair_for_main))

    def __recorder_of(self, element) -> ListElementRecorder:
        return self.recorder.recording_of(element)

    def _do_record_and_return_sh(self, element):
        return self._do_record_and_return(element,
                                          sh.new_sh_success())

    def _do_cleanup_main(self, first_value_of_pair_for_main):
        def ret_val(environment, os_services, previous_phase, *args):
            element = (first_value_of_pair_for_main, previous_phase)
            self.recorder.recording_of(element).record()
            return sh.new_sh_success()

        return ret_val

    def _do_record_and_return_svh(self, element):
        return self._do_record_and_return(element,
                                          svh.new_svh_success())

    def _do_record_and_return(self, element, return_value):
        def ret_val(*args):
            self.recorder.recording_of(element).record()
            return return_value

        return ret_val

    def _do_record_first_invokation(self, element):
        class RetVal:
            def __init__(self, recorder: ListRecorder):
                self.recorder = recorder
                self.has_recorded = False

            def __call__(self, *args, **kwargs):
                if not self.has_recorded:
                    self.recorder.recording_of(element).record()
                    self.has_recorded = True

        return RetVal(self.recorder)
