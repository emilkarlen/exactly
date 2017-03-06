import pathlib

from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds


class FileRefValidatorBase(PreOrPostSdsValidator):
    """
    Validates existence of the resolved path of a `FileRef`.
    """

    def __init__(self,
                 file_ref: FileRef):
        self.file_ref = file_ref

    def _validate_path(self, file_path: pathlib.Path) -> str:
        """
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        if self.file_ref.exists_pre_sds(environment.value_definitions):
            return self._validate_path(self.file_ref.file_path_pre_sds(environment))
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        if not self.file_ref.exists_pre_sds(environment.value_definitions):
            return self._validate_path(self.file_ref.file_path_post_sds(environment))
        return None
