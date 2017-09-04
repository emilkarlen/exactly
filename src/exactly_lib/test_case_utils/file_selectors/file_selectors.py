import pathlib

from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util import dir_contents_selection


class FileMatcherFromSelectors(FileMatcher):
    """Selects files from a directory according the a file condition."""

    def __init__(self, selectors: dir_contents_selection.Selectors):
        self._selectors = selectors

    @property
    def selectors(self) -> dir_contents_selection.Selectors:
        return self._selectors

    def select_from(self, directory: pathlib.Path) -> iter:
        """
        :param directory: An existing directory
        :return: Name of files in the given directory
        """
        return dir_contents_selection.get_selection(directory,
                                                    self._selectors)


SELECT_ALL_FILES = FileMatcherFromSelectors(dir_contents_selection.Selectors())


class FileSelectorStructureVisitor:
    """
    Visits all variants of :class:`FileSelector`.

    The existence of this class means that the structure of :class:`FileSelector`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.
    """

    def visit(self, file_selector: FileMatcher):
        if isinstance(file_selector, FileMatcherFromSelectors):
            return self.visit_selectors(file_selector.selectors)
        else:
            raise TypeError('Unknown {}: {}'.format(FileMatcher,
                                                    str(file_selector)))

    def visit_selectors(self, selectors: dir_contents_selection.Selectors):
        raise NotImplementedError('abstract method')
