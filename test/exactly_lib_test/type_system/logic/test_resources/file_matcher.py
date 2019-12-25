from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.err_msg.prop_descr import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult


class FileMatcherModelThatMustNotBeAccessed(FileMatcherModel):
    @property
    def path(self) -> DescribedPath:
        raise NotImplementedError('must not be used')

    @property
    def file_descriptor(self) -> FilePropertyDescriptorConstructor:
        raise NotImplementedError('must not be used')


class FileMatcherThatSelectsAllFilesTestImpl(MatcherImplBase[FileMatcherModel]):

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return self._new_tb().build_result(True)
