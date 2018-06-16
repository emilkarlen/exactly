from typing import Sequence


class FileWriteDistributor:
    """
    Forwards writing to multiple file objects
    """

    def __init__(self, files: Sequence):
        """
        :param files: Sequence of file objects that support write(str) -> int.
        """
        self._files = files

    def write(self, s: str) -> int:
        ret_val = None
        for f in self._files:
            n = f.write(s)
            if ret_val is None:
                ret_val = n
        return 0 if ret_val is None else ret_val
