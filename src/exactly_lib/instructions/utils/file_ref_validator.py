import pathlib

from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.value_definition.concrete_values import FileRefResolver
from exactly_lib.value_definition.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds


class FileRefValidatorBase(PreOrPostSdsValidator):
    """
    Validates existence of the resolved path of a `FileRef`.
    """

    def __init__(self,
                 file_ref_resolver: FileRefResolver):
        self._file_ref_resolver = file_ref_resolver

    def _validate_path(self, file_path: pathlib.Path) -> str:
        """
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        fr = self._file_ref_resolver.resolve(environment.value_definitions)
        if fr.exists_pre_sds():
            return self._validate_path(fr.file_path_pre_sds(environment.home_dir_path))
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        fr = self._file_ref_resolver.resolve(environment.value_definitions)
        if not fr.exists_pre_sds():
            return self._validate_path(fr.file_path_post_sds(environment.sds))
        return None
