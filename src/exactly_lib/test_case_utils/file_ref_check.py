from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironmentPreSds
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.err_msg2.path_impl import described_path_resolvers
from exactly_lib.test_case_utils.file_properties import FilePropertiesCheck, CheckResult
from exactly_lib.test_case_utils.file_ref_validator import FileRefValidatorBase


class FileRefCheck:
    def __init__(self,
                 file_ref_resolver: FileRefResolver,
                 check: FilePropertiesCheck):
        self.file_ref_resolver = file_ref_resolver
        self.file_properties = check

    def pre_sds_condition_result(self, environment: PathResolvingEnvironmentPreSds) -> CheckResult:
        fr = self.file_ref_resolver.resolve(environment.symbols)
        return self.file_properties.apply(fr.value_pre_sds(environment.hds))

    def post_sds_condition_result(self, environment: PathResolvingEnvironmentPostSds) -> CheckResult:
        fr = self.file_ref_resolver.resolve(environment.symbols)
        return self.file_properties.apply(fr.value_post_sds(environment.sds))

    def pre_or_post_sds_condition_result(self, environment: PathResolvingEnvironmentPreOrPostSds) -> CheckResult:
        fr = self.file_ref_resolver.resolve(environment.symbols)
        return self.file_properties.apply(fr.value_of_any_dependency(environment.home_and_sds))


class FileRefCheckValidator(FileRefValidatorBase):
    def __init__(self, file_ref_check: FileRefCheck):
        super().__init__(file_ref_check.file_ref_resolver)
        self.file_ref_check = file_ref_check

    def _validate_path(self, path: DescribedPathPrimitive) -> Optional[TextRenderer]:
        result = self.file_ref_check.file_properties.apply(path.primitive)
        if not result.is_success:
            return file_properties.FailureRenderer(result.cause,
                                                   path.describer)
        return None


def pre_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                    environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
    described_path = described_path_resolvers.of(file_ref_check.file_ref_resolver) \
        .resolve(environment.symbols) \
        .value_pre_sds(environment.hds)

    return _failure_message_or_none(file_ref_check.file_properties,
                                    described_path)


def post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                     environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
    described_path = described_path_resolvers.of(file_ref_check.file_ref_resolver) \
        .resolve(environment.symbols) \
        .value_post_sds__wo_hds(environment.sds)

    return _failure_message_or_none(file_ref_check.file_properties,
                                    described_path)


def pre_or_post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                            environment: PathResolvingEnvironmentPreOrPostSds
                                            ) -> Optional[TextRenderer]:
    described_path = described_path_resolvers.of(file_ref_check.file_ref_resolver) \
        .resolve(environment.symbols) \
        .value_of_any_dependency(environment.home_and_sds)

    return _failure_message_or_none(file_ref_check.file_properties,
                                    described_path)


def pre_sds_validate(file_ref_check: FileRefCheck,
                     environment: PathResolvingEnvironmentPreSds) -> svh.SuccessOrValidationErrorOrHardError:
    mb_failure = pre_sds_failure_message_or_none(file_ref_check,
                                                 environment)
    return (
        svh.new_svh_success()
        if mb_failure is None
        else svh.new_svh_validation_error(mb_failure)
    )


def pre_or_post_sds_validate(file_ref_check: FileRefCheck,
                             environment: PathResolvingEnvironmentPreOrPostSds
                             ) -> svh.SuccessOrValidationErrorOrHardError:
    mb_failure = pre_or_post_sds_failure_message_or_none(file_ref_check, environment)
    return (
        svh.new_svh_success()
        if mb_failure is None
        else svh.new_svh_validation_error(mb_failure)
    )


def _failure_message_or_none(check: FilePropertiesCheck,
                             path: DescribedPathPrimitive) -> Optional[TextRenderer]:
    result = check.apply(path.primitive)

    if result.is_success:
        return None
    else:
        return file_properties.FailureRenderer(result.cause,
                                               path.describer)
