import pathlib

from exactly_lib.instructions.utils.file_properties import FilePropertiesCheck, CheckResult
from exactly_lib.instructions.utils.file_properties import render_failure
from exactly_lib.instructions.utils.file_ref import FileRef, FileRefValidatorBase
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure


class FileRefCheck:
    def __init__(self,
                 file_reference: FileRef,
                 file_properties: FilePropertiesCheck):
        self.file_reference = file_reference
        self.file_properties = file_properties

    def pre_sds_condition_result(self, home_dir_path: pathlib.Path) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_pre_sds(home_dir_path))

    def post_sds_condition_result(self, sds: SandboxDirectoryStructure) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_post_sds(sds))

    def pre_or_post_sds_condition_result(self, home_and_sds: HomeAndSds) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_pre_or_post_sds(home_and_sds))


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


def pre_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                    home_dir_path: pathlib.Path) -> str:
    validation_result = file_ref_check.pre_sds_condition_result(home_dir_path)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_sds(home_dir_path)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                     sds: SandboxDirectoryStructure) -> str:
    validation_result = file_ref_check.post_sds_condition_result(sds)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_post_sds(sds)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_or_post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                            home_and_sds: HomeAndSds) -> str:
    validation_result = file_ref_check.pre_or_post_sds_condition_result(home_and_sds)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_or_post_sds(home_and_sds)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_sds_validate(file_ref_check: FileRefCheck,
                     environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
    validation_result = file_ref_check.pre_sds_condition_result(environment.home_directory)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_sds(environment.home_directory)
        return svh.new_svh_validation_error(render_failure(validation_result.cause,
                                                           file_path))
    return svh.new_svh_success()


def pre_or_post_sds_validate(file_ref_check: FileRefCheck,
                             home_and_sds: HomeAndSds) -> svh.SuccessOrValidationErrorOrHardError:
    failure_message = pre_or_post_sds_failure_message_or_none(file_ref_check, home_and_sds)
    if failure_message is not None:
        return svh.new_svh_validation_error(failure_message)
    return svh.new_svh_success()
