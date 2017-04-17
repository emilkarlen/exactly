import pathlib

from exactly_lib.instructions.utils.file_properties import FilePropertiesCheck, CheckResult
from exactly_lib.instructions.utils.file_properties import render_failure
from exactly_lib.instructions.utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironmentPreSds
from exactly_lib.test_case.phases.result import svh


class FileRefCheck:
    def __init__(self,
                 file_ref_resolver: FileRefResolver,
                 file_properties: FilePropertiesCheck):
        self.file_ref_resolver = file_ref_resolver
        self.file_properties = file_properties

    def pre_sds_condition_result(self, environment: PathResolvingEnvironmentPreSds) -> CheckResult:
        fr = self.file_ref_resolver.resolve(environment.value_definitions)
        return self.file_properties.apply(fr.file_path_pre_sds(environment.home_dir_path))

    def post_sds_condition_result(self, environment: PathResolvingEnvironmentPostSds) -> CheckResult:
        fr = self.file_ref_resolver.resolve(environment.value_definitions)
        return self.file_properties.apply(fr.file_path_post_sds(environment.sds))

    def pre_or_post_sds_condition_result(self, environment: PathResolvingEnvironmentPreOrPostSds) -> CheckResult:
        fr = self.file_ref_resolver.resolve(environment.value_definitions)
        return self.file_properties.apply(fr.file_path_pre_or_post_sds(environment.home_and_sds))


class FileRefCheckValidator(FileRefValidatorBase):
    def __init__(self, file_ref_check: FileRefCheck):
        super().__init__(file_ref_check.file_ref_resolver)
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
        fr = file_ref_check.file_ref_resolver.resolve(environment.value_definitions)
        file_path = fr.file_path_pre_sds(environment.home_dir_path)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                     environment: PathResolvingEnvironmentPostSds) -> str:
    validation_result = file_ref_check.post_sds_condition_result(environment)
    if not validation_result.is_success:
        fr = file_ref_check.file_ref_resolver.resolve(environment.value_definitions)
        file_path = fr.file_path_post_sds(environment.sds)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_or_post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                            environment: PathResolvingEnvironmentPreOrPostSds) -> str:
    validation_result = file_ref_check.pre_or_post_sds_condition_result(environment)
    if not validation_result.is_success:
        fr = file_ref_check.file_ref_resolver.resolve(environment.value_definitions)
        file_path = fr.file_path_pre_or_post_sds(environment.home_and_sds)
        return render_failure(validation_result.cause,
                              file_path)
    return None


def pre_sds_validate(file_ref_check: FileRefCheck,
                     environment: PathResolvingEnvironmentPreSds) -> svh.SuccessOrValidationErrorOrHardError:
    validation_result = file_ref_check.pre_sds_condition_result(environment)
    if not validation_result.is_success:
        fr = file_ref_check.file_ref_resolver.resolve(environment.value_definitions)
        file_path = fr.file_path_pre_sds(environment.home_dir_path)
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
