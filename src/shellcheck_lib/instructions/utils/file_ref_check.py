import pathlib

from shellcheck_lib.instructions.utils.file_properties import FilePropertiesCheck, CheckResult
from shellcheck_lib.instructions.utils.file_ref import FileRef
from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib.instructions.utils.file_properties import render_failure
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import svh


class FileRefCheck:
    def __init__(self,
                 file_reference: FileRef,
                 file_properties: FilePropertiesCheck):
        self.file_reference = file_reference
        self.file_properties = file_properties

    def pre_eds_condition_result(self, home_dir_path: pathlib.Path) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_pre_eds(home_dir_path))

    def post_eds_condition_result(self, home_and_eds: HomeAndEds) -> CheckResult:
        return self.file_properties.apply(self.file_reference.file_path_post_eds(home_and_eds))


def pre_eds_failure_message_or_none(file_ref_check: FileRefCheck,
                                    environment: GlobalEnvironmentForPreEdsStep) -> str:
    validation_result = file_ref_check.pre_eds_condition_result(environment.home_directory)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_pre_eds(environment.home_directory)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def post_eds_failure_message_or_none(file_ref_check: FileRefCheck,
                                     environment: GlobalEnvironmentForPostEdsPhase) -> str:
    validation_result = file_ref_check.post_eds_condition_result(environment.home_and_eds)
    if not validation_result.is_success:
        file_path = file_ref_check.file_reference.file_path_post_eds(environment.home_and_eds)
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


def post_eds_validate(file_ref_check: FileRefCheck,
                      environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
    failure_message = post_eds_failure_message_or_none(file_ref_check, environment)
    if failure_message is not None:
        return svh.new_svh_validation_error(failure_message)
    return svh.new_svh_success()
