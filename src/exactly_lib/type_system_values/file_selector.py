import pathlib


class FileSelector:
    """Selects files from a directory according the a file condition."""

    def select_from(self, directory: pathlib.Path) -> iter:
        raise NotImplementedError('abstract method')
