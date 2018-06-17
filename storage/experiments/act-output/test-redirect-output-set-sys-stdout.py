import pathlib
import subprocess
import sys

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


out_file_path = pathlib.Path('out') / 'stdout.txt'

saved_stdout = sys.stdout

with out_file_path.open(mode='a') as stdout_persist_file:
    fwd = FileWriteDistributor([sys.stdout, sys.stdout, stdout_persist_file])
    sys.stdout = fwd
    p = subprocess.Popen([sys.executable, 'print-to-stdout-err.py'],
                         stdout=subprocess.PIPE,
                         # stderr=subprocess.DEVNULL,
                         )

sys.stdout = saved_stdout

print('---after--------------------')
with out_file_path.open(mode='r') as stdout_persist_file:
    print(stdout_persist_file.read())
