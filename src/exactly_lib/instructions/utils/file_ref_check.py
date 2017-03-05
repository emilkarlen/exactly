import pathlib

from exactly_lib.instructions.utils.file_properties import FilePropertiesCheck, CheckResult
from exactly_lib.instructions.utils.file_properties import render_failure
from exactly_lib.instructions.utils.file_ref import FileRef, FileRefValidatorBase
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironmentPreSds
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh


class FileRefCheck:
    def __init__(self,
                 file_reference: FileRef,
                 file_properties: FilePropertiesCheck):
        self.file_reference = file_reference
        self.file_properties = file_properties

    def pre_sds_condition_result(self, environment: PathResolvingEnvironmentPreSds) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_pre_sds(environment))

    def post_sds_condition_result(self, environment: PathResolvingEnvironmentPostSds) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_post_sds(environment))

    def pre_or_post_sds_condition_result(self, environment: PathResolvingEnvironmentPreOrPostSds) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_pre_or_post_sds(environment))


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
                                    environment: PathResolvingEnvironmentPreSds) -> str:
    validation_result = file_ref_check.pre_sds_condition_result(environment)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_sds(environment)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                     environment: PathResolvingEnvironmentPostSds) -> str:
    validation_result = file_ref_check.post_sds_condition_result(environment)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_post_sds(environment)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_or_post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                            environment: PathResolvingEnvironmentPreOrPostSds) -> str:
    validation_result = file_ref_check.pre_or_post_sds_condition_result(environment)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_or_post_sds(environment)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_sds_validate(file_ref_check: FileRefCheck,
                     environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
    validation_result = file_ref_check.pre_sds_condition_result(environment.path_resolving_environment)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_sds(environment.path_resolving_environment)
        return svh.new_svh_validation_error(render_failure(validation_result.cause,
                                                           file_path))
    return svh.new_svh_success()


def pre_or_post_sds_validate(file_ref_check: FileRefCheck,
                             environment: PathResolvingEnvironmentPreOrPostSds
                             ) -> svh.SuccessOrValidationErrorOrHardError:
    failure_message = pre_or_post_sds_failure_message_or_none(file_ref_check, environment)
    if failure_message is not None:
        return svh.new_svh_validation_error(failure_message)
    return svh.new_svh_success()
