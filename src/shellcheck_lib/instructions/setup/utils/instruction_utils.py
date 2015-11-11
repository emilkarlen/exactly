from shellcheck_lib.instructions.utils.file_properties import render_failure
from shellcheck_lib.instructions.utils.file_ref_check import FileRefCheck
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction


class InstructionWithFileRefsBase(SetupPhaseInstruction):
    def __init__(self,
                 file_ref_check_list_tuple: tuple):
        """
        :param file_ref_check_list_tuple: [FileRefCheck] Sequence of files to be validates
        """
        self.file_ref_check_list_tuple = file_ref_check_list_tuple

    def pre_validate(self, environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        for file_ref_check in self.file_ref_check_list_tuple:
            assert isinstance(file_ref_check, FileRefCheck)
            validation_result = file_ref_check.pre_eds_condition_result(environment.home_directory)
            if validation_result and not validation_result.is_success:
                file_path = file_ref_check.file_reference.file_path_pre_eds(environment.home_directory)
                return svh.new_svh_validation_error(render_failure(validation_result.cause,
                                                                   file_path))
        return svh.new_svh_success()

    def post_validate(self,
                      environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        for file_ref_check in self.file_ref_check_list_tuple:
            assert isinstance(file_ref_check, FileRefCheck)
            validation_result = file_ref_check.post_eds_condition_result(environment.home_and_eds)
            if validation_result and not validation_result.is_success:
                file_path = file_ref_check.file_reference.file_path_post_eds(environment.home_and_eds)
                return svh.new_svh_validation_error(render_failure(validation_result.cause,
                                                                   file_path))
        return svh.new_svh_success()
