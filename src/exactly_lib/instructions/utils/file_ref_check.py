import pathlib

from exactly_lib.instructions.utils.file_properties import FilePropertiesCheck, CheckResult
from exactly_lib.instructions.utils.file_properties import render_failure
from exactly_lib.instructions.utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironmentPreSds
from exactly_lib.value_definition.concrete_values import FileRefValue


class FileRefCheck:
    def __init__(self,
                 file_reference: FileRefValue,
                 file_properties: FilePropertiesCheck):
        self.file_reference = file_reference
        self.file_properties = file_properties

    def pre_sds_condition_result(self, environment: PathResolvingEnvironmentPreSds) -> CheckResult:
        fr = self.file_reference.resolve(environment.value_definitions)
        return self.file_properties.apply(fr.file_path_pre_sds(environment))

    def post_sds_condition_result(self, environment: PathResolvingEnvironmentPostSds) -> CheckResult:
        fr = self.file_reference.resolve(environment.value_definitions)
        return self.file_properties.apply(fr.file_path_post_sds(environment))

    def pre_or_post_sds_condition_result(self, environment: PathResolvingEnvironmentPreOrPostSds) -> CheckResult:
        fr = self.file_reference.resolve(environment.value_definitions)
        return self.file_properties.apply(fr.file_path_pre_or_post_sds(environment))


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
        fr = file_ref_check.file_reference.resolve(environment.value_definitions)
        file_path = fr.file_path_pre_sds(environment)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                     environment: PathResolvingEnvironmentPostSds) -> str:
    validation_result = file_ref_check.post_sds_condition_result(environment)
    if not validation_result.is_success:
        fr = file_ref_check.file_reference.resolve(environment.value_definitions)
        file_path = fr.file_path_post_sds(environment)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_or_post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                            environment: PathResolvingEnvironmentPreOrPostSds) -> str:
    validation_result = file_ref_check.pre_or_post_sds_condition_result(environment)
    if not validation_result.is_success:
        fr = file_ref_check.file_reference.resolve(environment.value_definitions)
        file_path = fr.file_path_pre_or_post_sds(environment)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_sds_validate(file_ref_check: FileRefCheck,
                     environment: PathResolvingEnvironmentPreSds) -> svh.SuccessOrValidationErrorOrHardError:
    validation_result = file_ref_check.pre_sds_condition_result(environment)
    if not validation_result.is_success:
        fr = file_ref_check.file_reference.resolve(environment.value_definitions)
        file_path = fr.file_path_pre_sds(environment)
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
