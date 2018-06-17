import pathlib
import selectors
import subprocess
import sys
import time
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
            f.flush()
            if ret_val is None:
                ret_val = n
        return 0 if ret_val is None else ret_val


class CopyMaker:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def handle_chunk(self):
        self.dst.write(self.src.read())


def msg(s: str):
    sys.stderr.write(s)
    sys.stderr.write('\n')
    sys.stderr.flush()


class Processor:
    def __init__(self,
                 process: subprocess.Popen,
                 stdout_writer: FileWriteDistributor,
                 stderr_writer: FileWriteDistributor,
                 ):
        self.process = process

        self.stdout_copy_maker = CopyMaker(process.stdout, stdout_writer)
        self.stderr_copy_maker = CopyMaker(process.stderr, stderr_writer)

        self.selector = selectors.DefaultSelector()

        self.selector.register(process.stdout, selectors.EVENT_READ, self.stdout_copy_maker)
        self.selector.register(process.stderr, selectors.EVENT_READ, self.stderr_copy_maker)

    def _handle_done(self):
        self.stdout_copy_maker.handle_chunk()
        self.stderr_copy_maker.handle_chunk()
        self.selector.close()

    def run_with_timeout(self, timeout: int) -> int:
        start_time = time.perf_counter()

        while self.process.poll() is None:
            seconds_executed = int(time.perf_counter() - start_time) + 1
            seconds_left = max(1, timeout - seconds_executed)
            msg('seconds left=' + str(seconds_left))
            try:
                events = self.selector.select(timeout=seconds_left)
                for key, mask in events:
                    copy_maker = key.data
                    copy_maker.handle_chunk()
            except TimeoutError as ex:
                self._handle_done()
                self.process.kill()
                raise ex

        self._handle_done()
        return self.process.returncode


out_file_path = pathlib.Path('out') / 'stdout.txt'
err_file_path = pathlib.Path('out') / 'stderr.txt'


def run(source_file: str,
        timeout: int):
    with out_file_path.open(mode='w') as stdout_persist_file:
        with err_file_path.open(mode='w') as stderr_persist_file:
            stdout_writer = FileWriteDistributor([sys.stdout, stdout_persist_file])
            stderr_writer = FileWriteDistributor([sys.stderr, stderr_persist_file])

            p = subprocess.Popen([sys.executable, source_file],
                                 universal_newlines=True,
                                 bufsize=0,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 )
            processor = Processor(p, stdout_writer, stderr_writer)
            try:
                exit_code = processor.run_with_timeout(timeout)
                print('exit code=' + str(exit_code))
            except TimeoutError as ex:
                print('timeout=' + str(ex))


def print_file(path: pathlib.Path):
    with path.open(mode='r') as f:
        sys.stdout.write(f.read())


def main(source_file: str):
    run(source_file, timeout=3)
    print('---after--------------------')
    print('-----out--------------------')
    print_file(out_file_path)
    print('-----err--------------------')
    print_file(err_file_path)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: PYTHON-PROGRAM\n')
        sys.exit(1)
    py_src_file = pathlib.Path(sys.argv[1])
    if not py_src_file.is_file():
        sys.stderr.write('Not a file: ' + str(py_src_file) + '\n')
        sys.exit(1)
    main(str(py_src_file))
