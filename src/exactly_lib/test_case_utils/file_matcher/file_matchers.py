import pathlib

from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util import dir_contents_selection


class FileMatcherFromSelectors(FileMatcher):
    """Selects files from a directory according the a file condition."""

    def __init__(self, selectors: dir_contents_selection.Selectors):
        self._selectors = selectors

    @property
    def option_description(self) -> str:
        return 'selectors - this class should be removes'

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

    def matches(self, path: pathlib.Path) -> bool:
        raise NotImplementedError('this method should never be used, since this class should be refactored away')


class FileMatcherConstant(FileMatcher):
    """Selects files from a directory according the a file condition."""

    def __init__(self, result: bool):
        self._result = result

    @property
    def result_constant(self) -> bool:
        return self._result

    @property
    def option_description(self) -> str:
        return 'any file' if self._result else 'no file'

    def select_from(self, directory: pathlib.Path) -> iter:
        raise NotImplementedError('this method should never be used, since this method should be refactored away')

    def matches(self, path: pathlib.Path) -> bool:
        return self._result


SELECT_ALL_FILES = FileMatcherFromSelectors(dir_contents_selection.Selectors())


class FileMatcherStructureVisitor:
    """
    Visits all variants of :class:`FileMatcher`.

    The existence of this class means that the structure of :class:`FileMatcher`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.
    """

    def visit(self, matcher: FileMatcher):
        if isinstance(matcher, FileMatcherFromSelectors):
            return self.visit_selectors(matcher)
        if isinstance(matcher, FileMatcherConstant):
            return self.visit_constant(matcher)
        else:
            raise TypeError('Unknown {}: {}'.format(FileMatcher,
                                                    str(matcher)))

    def visit_constant(self, matcher: FileMatcherConstant):
        raise NotImplementedError('abstract method')

    def visit_selectors(self, matcher: FileMatcherFromSelectors):
        raise NotImplementedError('abstract method')
