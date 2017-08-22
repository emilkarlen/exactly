import pathlib

from exactly_lib.util import dir_contents_selection


class FileSelector:
    """Selects files from a directory according the a file condition."""

    def __init__(self, selectors: dir_contents_selection.Selectors):
        self._selectors = selectors

    def select_from(self, directory: pathlib.Path) -> iter:
        """
        :param directory: An existing directory
        :return: Name of files in the given directory
        """
        dir_contents_selection.get_selection(directory,
                                             self._selectors)
