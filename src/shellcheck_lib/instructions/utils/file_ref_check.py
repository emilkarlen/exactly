import pathlib

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.instructions.utils.file_properties import FilePropertiesCheck, CheckResult
from shellcheck_lib.instructions.utils.file_properties import render_failure
from shellcheck_lib.instructions.utils.file_ref import FileRef, FileRefValidatorBase
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib.test_case.sections.result import svh


class FileRefCheck:
    def __init__(self,
                 file_reference: FileRef,
                 file_properties: FilePropertiesCheck):
        self.file_reference = file_reference
        self.file_properties = file_properties

    def pre_eds_condition_result(self, home_dir_path: pathlib.Path) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_pre_eds(home_dir_path))

    def post_eds_condition_result(self, eds: ExecutionDirectoryStructure) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_post_eds(eds))

    def pre_or_post_eds_condition_result(self, home_and_eds: HomeAndEds) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_pre_or_post_eds(home_and_eds))


class FileRefCheckValidator(FileRefValidatorBase):
    def __init__(self, file_ref_check: FileRefCheck):
        super().__init__(file_ref_check.file_reference)
        self.file_ref_check = file_ref_check

    def _validate_path(self, file_path: pathlib.Path) -> str:
        result = self.file_ref_check.file_properties.apply(file_path)
        if not result.is_success:
            return render_failure(result.cause,
                                  file_path)
        return None


def pre_eds_failure_message_or_none(file_ref_check: FileRefCheck,
                                    home_dir_path: pathlib.Path) -> str:
    validation_result = file_ref_check.pre_eds_condition_result(home_dir_path)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_eds(home_dir_path)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def post_eds_failure_message_or_none(file_ref_check: FileRefCheck,
                                     eds: ExecutionDirectoryStructure) -> str:
    validation_result = file_ref_check.post_eds_condition_result(eds)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_post_eds(eds)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_or_post_eds_failure_message_or_none(file_ref_check: FileRefCheck,
                                            home_and_eds: HomeAndEds) -> str:
    validation_result = file_ref_check.pre_or_post_eds_condition_result(home_and_eds)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_or_post_eds(home_and_eds)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_eds_validate(file_ref_check: FileRefCheck,
                     environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
    validation_result = file_ref_check.pre_eds_condition_result(environment.home_directory)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_eds(environment.home_directory)
        return svh.new_svh_validation_error(render_failure(validation_result.cause,
                                                           file_path))
    return svh.new_svh_success()


def pre_or_post_eds_validate(file_ref_check: FileRefCheck,
                             home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
    failure_message = pre_or_post_eds_failure_message_or_none(file_ref_check, home_and_eds)
    if failure_message is not None:
        return svh.new_svh_validation_error(failure_message)
    return svh.new_svh_success()
