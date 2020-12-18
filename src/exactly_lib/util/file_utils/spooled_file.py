import io as _io
import pathlib
from typing import Callable, Iterable


class SpooledTextFile(_io.TextIOBase):
    """Temporary text file wrapper, specialized to switch from
    or StringIO to a real file when it exceeds a certain size or
    when a fileno is needed.

    Lines are ended by '\n'.

    Not every part of the TextIO interface is implemented.

    Large parts copied from tempfile.SpooledTemporaryFile.
    """

    def __init__(self,
                 mem_buff_size: int,
                 get_unused_path: Callable[[], pathlib.Path],
                 ):
        """
        :param mem_buff_size: The size of the memory buffer.
        If the size of contents written to the file exceeds this size,
        a file on disk is created.

        :param get_unused_path: Gives an unused path used for creating
        a file on disk (if needed, or requested via "fileno").
        The path is opened for exclusive creation, read and write.
        """
        self._max_size = mem_buff_size
        self._get_unused_path = get_unused_path
        self._path = None
        # Setting newline="\n" avoids newline translation;
        # this is important because otherwise on Windows we'd
        # get double newline translation upon rollover().
        self._file = _io.StringIO(newline="\n")

    # Context management protocol
    def __enter__(self):
        if self._file.closed:
            raise ValueError("Cannot enter context with closed file")
        return self

    def __exit__(self, exc, value, tb):
        self._file.close()

    # file protocol
    def __iter__(self):
        return self._file.__iter__()

    @property
    def closed(self) -> bool:
        return self._file.closed

    def isatty(self) -> bool:
        return False

    def seekable(self) -> bool:
        return True

    @property
    def encoding(self):
        raise _io.UnsupportedOperation()

    @property
    def mode(self):
        raise _io.UnsupportedOperation()

    @property
    def newlines(self):
        raise _io.UnsupportedOperation()

    @property
    def is_mem_buff(self) -> bool:
        """Tells if the object is a memory buffer
        - no file on disk."""
        return self._path is None

    @property
    def is_file_on_disk(self) -> bool:
        return not self.is_mem_buff

    @property
    def path_of_file_on_disk(self) -> pathlib.Path:
        if self._path is None:
            raise ValueError('object does not represent a file on disk (it is a memory buffer)')
        else:
            return self._path

    @property
    def mem_buff(self) -> str:
        """Precondition: is_mem_buff"""
        if self._path is not None:
            raise ValueError('object does not represent a memory buffer (it is a file on disk)')
        return self._file.getvalue()

    def close(self):
        self._file.close()

    def fileno(self) -> int:
        """Converts from mem buff, to file on disk
        (if not already a file on disk).

        :returns the disk file's fileno
        """
        self._rollover()
        return self._file.fileno()

    def flush(self):
        self._file.flush()

    def read(self, *args) -> str:
        return self._file.read(*args)

    def readable(self) -> bool:
        return True

    def readline(self, *args) -> str:
        return self._file.readline(*args)

    def readlines(self, *args):
        return self._file.readlines(*args)

    def seek(self, *args):
        self._file.seek(*args)

    def tell(self) -> int:
        return self._file.tell()

    def truncate(self, size=None):
        if size is None:
            self._file.truncate()
        else:
            if size > self._max_size:
                self._rollover()
            self._file.truncate(size)

    def write(self, s: str):
        if self._path is None:
            file = self._file
            rv = file.write(s)
            self._check(file)
            return rv
        else:
            return self._file.write(s)

    def writelines(self, lines: Iterable[str]):
        if self._path is None:
            lines = iter(lines)
            max_size = self._max_size
            file = self._file
            for line in lines:
                file.write(line)
                if file.tell() > max_size:
                    self._rollover()
                    self._file.writelines(lines)
        else:
            self._file.writelines(lines)

    def _check(self, file):
        max_size = self._max_size
        if max_size and file.tell() > max_size:
            self._rollover()

    def _rollover(self):
        if self._path is not None:
            return
        file = self._file
        self._path = self._get_unused_path()
        newfile = self._file = self._path.open(mode='x+')
        newfile.write(file.getvalue())
        newfile.seek(file.tell(), 0)
