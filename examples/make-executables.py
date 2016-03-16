import os
import pathlib
import stat

import sys


def _msg(msg: str):
    sys.stderr.write(msg + os.linesep)


class SourceAndTarget(tuple):
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


class SourceAndTargetSetup(tuple):
    def __new__(cls,
                base_dir: pathlib.Path,
                source_and_target: SourceAndTarget):
        return tuple.__new__(cls, (base_dir, source_and_target))

    @property
    def base_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def source_and_target(self) -> SourceAndTarget:
        return self[1]

    @property
    def source(self) -> pathlib.Path:
        return self.base_dir / self.source_and_target.source

    @property
    def target(self) -> pathlib.Path:
        return self.base_dir / self.source_and_target.target

    @property
    def source_plain(self) -> pathlib.Path:
        return self.source_and_target.source

    @property
    def target_plain(self) -> pathlib.Path:
        return self.source_and_target.target


class UnixMake:
    def __init__(self,
                 suffix: str,
                 interpreter: str):
        self.suffix = suffix
        self.interpreter = interpreter

    def make(self,
             setup: SourceAndTargetSetup):
        if self._is_fresh(setup):
            return
        self._generate(setup)

    def make_all(self, base_dir: pathlib.Path,
                 setups: iter):
        for setup in setups:
            self.make(SourceAndTargetSetup(base_dir, setup))

    def clean(self,
              setup: SourceAndTargetSetup):
        if setup.target.exists():
            _msg('Removing: ' + str(setup.target_plain))
            setup.target.unlink()

    def clean_all(self, base_dir: pathlib.Path, setups: iter):
        for setup in setups:
            self.clean(SourceAndTargetSetup(base_dir, setup))

    def _is_fresh(self, setup: SourceAndTargetSetup):
        source_file = self._source_file(setup)
        ret_val = setup.target.is_file() and \
                  setup.target.stat().st_mtime >= source_file.stat().st_mtime
        if ret_val:
            _msg('Fresh: ' + str(setup.target_plain))
        return ret_val

    def _source_file(self, setup: SourceAndTargetSetup) -> pathlib.Path:
        ret_val = setup.source.with_suffix(self.suffix)
        if not ret_val.is_file():
            raise ValueError("Source does not exist: " + str(ret_val))
        return ret_val

    def _generate(self, setup: SourceAndTargetSetup):
        _msg('Making: ' + str(setup.target_plain))
        source_file = self._source_file(setup)
        with setup.target.open('w+') as target_file:
            self.write_executable_header(target_file)
            self._append_source(target_file,
                                source_file)
        self._make_executable(setup.target)

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


def _resolve_root(script_file_path_name: str) -> pathlib.Path:
    script_file_path = pathlib.Path(script_file_path_name)
    return script_file_path.resolve().parent


if __name__ == '__main__':
    base_dir = _resolve_root(sys.argv[0])
    base_dir = pathlib.Path.cwd().resolve()
    if not base_dir.is_dir():
        _msg('Cannot resolve root directory: ' + str(base_dir))
    _msg(str(base_dir))
    if len(sys.argv) != 3:
        _msg("Usage all|clean|test")
        sys.exit(1)

    maker = UnixMake('.py', sys.executable)
    ts = SourceAndTarget(pathlib.Path(sys.argv[1]),
                         pathlib.Path(sys.argv[2]))
    maker.make(SourceAndTargetSetup(base_dir, ts))
