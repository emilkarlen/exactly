from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironmentPreSds
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FilePropertiesCheck
from exactly_lib.test_case_utils.path_validator import PathSdvValidatorBase, PathDdvValidatorBase
from exactly_lib.type_system.data.path_ddv import DescribedPath, PathDdv


class PathCheck:
    def __init__(self,
                 path_sdv: PathSdv,
                 check: FilePropertiesCheck):
        self.path_sdv = path_sdv
        self.file_properties = check


class PathCheckDdv:
    def __init__(self,
                 path_ddv: PathDdv,
                 check: FilePropertiesCheck):
        self.path_ddv = path_ddv
        self.file_properties = check


class PathCheckValidator(PathSdvValidatorBase):
    def __init__(self, path_check: PathCheck):
        super().__init__(path_check.path_sdv)
        self.path_check = path_check

    def _validate_path(self, path: DescribedPath) -> Optional[TextRenderer]:
        result = self.path_check.file_properties.apply(path.primitive)
        if not result.is_success:
            return file_properties.FailureRenderer(result.cause,
                                                   path.describer)
        return None


class PathCheckDdvValidator(PathDdvValidatorBase):
    def __init__(self, path_check: PathCheckDdv):
        super().__init__(path_check.path_ddv)
        self.path_check = path_check

    def _validate_path(self, path: DescribedPath) -> Optional[TextRenderer]:
        result = self.path_check.file_properties.apply(path.primitive)
        if not result.is_success:
            return file_properties.FailureRenderer(result.cause,
                                                   path.describer)
        return None


def pre_sds_failure_message_or_none(path_check: PathCheck,
                                    environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
    described_path = (
        path_check.path_sdv.resolve(environment.symbols)
            .value_pre_sds__d(environment.hds)
    )

    return failure_message_or_none(path_check.file_properties,
                                   described_path)


def post_sds_failure_message_or_none(path_check: PathCheck,
                                     environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
    described_path = (
        path_check.path_sdv.resolve(environment.symbols)
            .value_post_sds__d(environment.sds)
    )

    return failure_message_or_none(path_check.file_properties,
                                   described_path)


def pre_or_post_sds_failure_message_or_none(path_check: PathCheck,
                                            environment: PathResolvingEnvironmentPreOrPostSds
                                            ) -> Optional[TextRenderer]:
    described_path = (
        path_check.path_sdv.resolve(environment.symbols)
            .value_of_any_dependency__d(environment.tcds)
    )

    return failure_message_or_none(path_check.file_properties,
                                   described_path)


def pre_sds_validate(path_check: PathCheck,
                     environment: PathResolvingEnvironmentPreSds) -> svh.SuccessOrValidationErrorOrHardError:
    return svh.new_maybe_svh_validation_error(
        pre_sds_failure_message_or_none(path_check,
                                        environment)
    )


def pre_or_post_sds_validate(path_check: PathCheck,
                             environment: PathResolvingEnvironmentPreOrPostSds
                             ) -> svh.SuccessOrValidationErrorOrHardError:
    return svh.new_maybe_svh_validation_error(
        pre_or_post_sds_failure_message_or_none(path_check, environment)
    )


def failure_message_or_none(check: FilePropertiesCheck,
                            path: DescribedPath) -> Optional[TextRenderer]:
    result = check.apply(path.primitive)

    return (
        None
        if result.is_success
        else file_properties.FailureRenderer(result.cause,
                                             path.describer)
    )
