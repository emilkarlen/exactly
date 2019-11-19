from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive


class PathValidatorBase(PreOrPostSdsValidator):
    """
    Validates existence of the resolved path of a `PathDdv`.
    """

    def __init__(self,
                 path_sdv: PathSdv):
        self._path_sdv = path_sdv

    def _validate_path(self, path: DescribedPathPrimitive) -> Optional[TextRenderer]:
        """
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        path_ddv = self._path_sdv.resolve(environment.symbols)
        if path_ddv.exists_pre_sds():
            return self._validate_path(path_ddv.value_pre_sds__d(environment.hds))
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        described_path_value = self._path_sdv.resolve(environment.symbols)
        if not described_path_value.exists_pre_sds():
            return self._validate_path(described_path_value.value_post_sds__d(environment.sds))
        return None
