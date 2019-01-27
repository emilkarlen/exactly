from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel


class FileMatcherThatSelectsAllFilesTestImpl(FileMatcher):
    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches(self, model: FileMatcherModel) -> bool:
        return True
