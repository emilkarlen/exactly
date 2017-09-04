import pathlib

from exactly_lib.type_system.logic.file_matcher import FileMatcher


class FileMatcherThatSelectsAllFilesTestImpl(FileMatcher):
    def select_from(self, directory: pathlib.Path) -> iter:
        return directory.iterdir()
