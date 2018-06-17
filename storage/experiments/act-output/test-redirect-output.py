import os
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


stdout_fd = os.dup(sys.stdout.fileno())
stdout_file = open(stdout_fd, mode='a', closefd=False)
sys.stderr.write(str(type(stdout_fd)) + '\n')

print('parent: print')
sys.stdout.write('parent: sys.stdout.write\n')
stdout_file.write('parent: stdout_file.write\n')

# stdout_f = io.StringIO()

out_file_path = pathlib.Path('out') / 'stdout.txt'
print('---exe sub process--------------------')

with out_file_path.open(mode='w') as stdout_persist_file:
    fwd = FileWriteDistributor([stdout_file, stdout_persist_file])
    exit_code = subprocess.call([sys.executable, 'print-to-stdout-err.py'],
                                timeout=20,
                                stdout=stdout_file,
                                stderr=subprocess.DEVNULL,
                                )

print('---after--------------------')
with out_file_path.open(mode='r') as stdout_persist_file:
    print(stdout_persist_file.read())
