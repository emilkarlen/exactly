import pathlib

from exactly_lib.type_system.file_selector import FileSelector


class FileSelectorThatSelectsAllFilesTestImpl(FileSelector):
    def select_from(self, directory: pathlib.Path) -> iter:
        return directory.iterdir()
