import pathlib

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import RelOptionType
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.util.symbol_table import SymbolTable


def file_ref_test_impl(file_name: str = 'file_ref_test_impl',
                       relativity: RelOptionType = RelOptionType.REL_RESULT) -> FileRef:
    return _FileRefTestImpl(file_name, relativity)


class _FileRefTestImpl(FileRef):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self, file_name: str, relativity: RelOptionType):
        super().__init__(file_name)
        self._relativity = relativity

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._relativity

    def value_references_of_paths(self) -> list:
        return []

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self._relativity == RelOptionType.REL_HOME

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return pathlib.Path('_FileRefWithoutValRef-path') / self.path_suffix_path(environment.value_definitions)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return pathlib.Path('_FileRefWithoutValRef-path') / self.path_suffix_path(environment.value_definitions)
