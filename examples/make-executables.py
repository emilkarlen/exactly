import os
import pathlib
import stat

import sys


def _msg(msg: str):
    sys.stderr.write(msg + os.linesep)


class TargetSetup(tuple):
    def __new__(cls,
                source: pathlib.Path,
                target: pathlib.Path):
        return tuple.__new__(cls, (source, target))

    @property
    def source(self) -> pathlib.Path:
        return self[0]

    @property
    def target(self) -> pathlib.Path:
        return self[1]


class UnixMake:
    def __init__(self,
                 suffix: str,
                 interpreter: str):
        self.suffix = suffix
        self.interpreter = interpreter

    def make(self,
             target_setup: TargetSetup):
        if self._is_fresh(target_setup):
            return
        self._generate(target_setup)

    def make_all(self, target_setups: iter):
        for target_setup in target_setups:
            self.make(target_setup)

    def clean(self,
              target_setup: TargetSetup):
        if target_setup.target.exists():
            _msg('Removing: ' + str(target_setup.target))
            target_setup.target.unlink()

    def clean_all(self, target_setups: iter):
        for target_setup in target_setups:
            self.clean(target_setup)

    def _is_fresh(self, target_setup: TargetSetup):
        source_file = self._source_file(target_setup)
        ret_val = target_setup.target.is_file() and \
                  target_setup.target.stat().st_mtime >= source_file.stat().st_mtime
        if ret_val:
            _msg('Fresh: ' + str(target_setup.target))
        return ret_val

    def _source_file(self, target_setup) -> pathlib.Path:
        ret_val = target_setup.source.with_suffix(self.suffix)
        if not ret_val.is_file():
            raise ValueError("Source does not exist: " + str(ret_val))
        return ret_val

    def _generate(self, target_setup: TargetSetup):
        source_file = self._source_file(target_setup)
        with target_setup.target.open('w+') as target_file:
            self.write_executable_header(target_file)
            self._append_source(target_file,
                                source_file)
        self._make_executable(target_setup.target)

    def write_executable_header(self, target_file):
        target_file.write(os.linesep.join(['#!' + self.interpreter,
                                           '',
                                           '']))

    @staticmethod
    def _make_executable(target: pathlib.Path):
        current_mode = target.stat().st_mode
        target.chmod(current_mode | stat.S_IEXEC)

    @staticmethod
    def _append_source(target_file, source: pathlib.Path):
        target_file.write(source.open().read())


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError("Usage SOURCE TARGET")
    maker = UnixMake('.py', sys.executable)
    ts = TargetSetup(pathlib.Path(sys.argv[1]),
                     pathlib.Path(sys.argv[2]))
    maker.make(ts)
