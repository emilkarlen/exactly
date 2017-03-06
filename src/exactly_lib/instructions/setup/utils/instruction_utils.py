from exactly_lib.instructions.utils.file_ref_check import FileRefCheck, pre_sds_validate, pre_or_post_sds_validate
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction


class InstructionWithFileRefsBase(SetupPhaseInstruction):
    def __init__(self,
                 file_ref_check_list_tuple: tuple):
        """
        :param file_ref_check_list_tuple: [FileRefCheck] Sequence of files to be validates
        """
        self.file_ref_check_list_tuple = file_ref_check_list_tuple

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        for file_ref_check in self.file_ref_check_list_tuple:
            assert isinstance(file_ref_check, FileRefCheck)
            if file_ref_check.file_reference.exists_pre_sds(environment.value_definitions):
                result = pre_sds_validate(file_ref_check, environment.path_resolving_environment)
                if not result.is_success:
                    return result
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        for file_ref_check in self.file_ref_check_list_tuple:
            assert isinstance(file_ref_check, FileRefCheck)
            if not file_ref_check.file_reference.exists_pre_sds(environment.value_definitions):
                result = pre_or_post_sds_validate(file_ref_check,
                                                  environment.path_resolving_environment_pre_or_post_sds)
                if not result.is_success:
                    return result
        return svh.new_svh_success()
