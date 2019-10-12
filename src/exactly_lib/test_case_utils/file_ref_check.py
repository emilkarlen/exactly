from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironmentPreSds
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FilePropertiesCheck
from exactly_lib.test_case_utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.type_system.data.file_ref import DescribedPathPrimitive


class FileRefCheck:
    def __init__(self,
                 file_ref_resolver: FileRefResolver,
                 check: FilePropertiesCheck):
        self.file_ref_resolver = file_ref_resolver
        self.file_properties = check


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
    described_path = (
        file_ref_check.file_ref_resolver.resolve(environment.symbols)
            .value_pre_sds__d(environment.hds)
    )

    return failure_message_or_none(file_ref_check.file_properties,
                                   described_path)


def post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                     environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
    described_path = (
        file_ref_check.file_ref_resolver.resolve(environment.symbols)
            .value_post_sds__d(environment.sds)
    )

    return failure_message_or_none(file_ref_check.file_properties,
                                   described_path)


def pre_or_post_sds_failure_message_or_none(file_ref_check: FileRefCheck,
                                            environment: PathResolvingEnvironmentPreOrPostSds
                                            ) -> Optional[TextRenderer]:
    described_path = (
        file_ref_check.file_ref_resolver.resolve(environment.symbols)
            .value_of_any_dependency__d(environment.home_and_sds)
    )

    return failure_message_or_none(file_ref_check.file_properties,
                                   described_path)


def pre_sds_validate(file_ref_check: FileRefCheck,
                     environment: PathResolvingEnvironmentPreSds) -> svh.SuccessOrValidationErrorOrHardError:
    return svh.new_maybe_svh_validation_error(
        pre_sds_failure_message_or_none(file_ref_check,
                                        environment)
    )


def pre_or_post_sds_validate(file_ref_check: FileRefCheck,
                             environment: PathResolvingEnvironmentPreOrPostSds
                             ) -> svh.SuccessOrValidationErrorOrHardError:
    return svh.new_maybe_svh_validation_error(
        pre_or_post_sds_failure_message_or_none(file_ref_check, environment)
    )


def failure_message_or_none(check: FilePropertiesCheck,
                            path: DescribedPathPrimitive) -> Optional[TextRenderer]:
    result = check.apply(path.primitive)

    return (
        None
        if result.is_success
        else file_properties.FailureRenderer(result.cause,
                                             path.describer)
    )
