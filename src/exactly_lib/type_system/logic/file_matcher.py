import pathlib


class WithOptionDescription:
    """Describes the option/config of an object"""

    @property
    def option_description(self) -> str:
        raise NotImplementedError('abstract method')


class FileMatcher(WithOptionDescription):
    """Matches a path of an existing file."""

    def select_from(self, directory: pathlib.Path) -> iter:
        raise NotImplementedError('abstract method')

    def matches(self, path: pathlib.Path) -> bool:
        """
        :param path: The path of an existing file (but may be a broken symbolic link).
        """
        raise NotImplementedError('abstract method')
