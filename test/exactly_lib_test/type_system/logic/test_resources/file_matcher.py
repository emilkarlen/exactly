from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.type_system.data.file_ref import DescribedPathPrimitive
from exactly_lib.type_system.err_msg.prop_descr import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.file_utils import TmpDirFileSpace


class FileMatcherModelThatMustNotBeAccessed(FileMatcherModel):
    @property
    def tmp_file_space(self) -> TmpDirFileSpace:
        raise NotImplementedError('must not be used')

    @property
    def path(self) -> DescribedPathPrimitive:
        raise NotImplementedError('must not be used')

    @property
    def file_descriptor(self) -> FilePropertyDescriptorConstructor:
        raise NotImplementedError('must not be used')


class FileMatcherThatSelectsAllFilesTestImpl(FileMatcherImplBase):

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches(self, model: FileMatcherModel) -> bool:
        return True

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return self._new_tb().build_result(True)
