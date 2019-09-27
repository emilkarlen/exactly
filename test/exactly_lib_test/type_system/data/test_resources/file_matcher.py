from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel


class FileMatcherThatSelectsAllFilesTestImpl(FileMatcherImplBase):

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches(self, model: FileMatcherModel) -> bool:
        return True
