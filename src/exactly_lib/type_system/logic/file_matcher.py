import pathlib


class FileMatcher:
    """Matches a path of an existing file."""

    def select_from(self, directory: pathlib.Path) -> iter:
        raise NotImplementedError('abstract method')

    def matches(self, path: pathlib.Path) -> bool:
        """
        :param path: The path of an existing file (but may be a broken symbolic link).
        """
        raise NotImplementedError('abstract method')
