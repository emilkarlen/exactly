import pathlib

from exactly_lib.type_system.logic.file_matcher import FileMatcher


class FileMatcherThatSelectsAllFilesTestImpl(FileMatcher):
    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches(self, path: pathlib.Path) -> bool:
        return True
