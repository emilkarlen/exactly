from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileTypeAccess
from exactly_lib.type_system.logic.matching_result import MatchingResult


class FileMatcherModelThatMustNotBeAccessed(FileMatcherModel):
    @property
    def path(self) -> DescribedPath:
        raise NotImplementedError('must not be used')

    @property
    def file_type_access(self) -> FileTypeAccess:
        raise NotImplementedError('must not be used')


class FileMatcherThatSelectsAllFilesTestImpl(MatcherImplBase[FileMatcherModel]):

    @property
    def name(self) -> str:
        return str(type(self))

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return self._new_tb().build_result(True)
