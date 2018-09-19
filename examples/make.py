import sys

import os
import stat
from pathlib import Path
from typing import List, Tuple, Iterable


class SourceAndTarget(tuple):
    def __new__(cls,
                source: Path,
                target: Path):
        return tuple.__new__(cls, (source, target))

    @property
    def source(self) -> Path:
        return self[0]

    @property
    def target(self) -> Path:
        return self[1]


class SourceAndTargetSetup(tuple):
    def __new__(cls,
                base_dir: Path,
                installation_sub_dir: str,
                source_and_target: SourceAndTarget):
        return tuple.__new__(cls, (base_dir,
                                   Path(installation_sub_dir),
                                   source_and_target))

    @property
    def base_dir(self) -> Path:
        return self[0]

    @property
    def installation_sub_dir(self) -> Path:
        return self[1]

    @property
    def installation_dir(self) -> Path:
        return self.base_dir / self.installation_sub_dir

    @property
    def source_and_target(self) -> SourceAndTarget:
        return self[2]

    @property
    def source(self) -> Path:
        return self.base_dir / self.source_and_target.source

    @property
    def target(self) -> Path:
        return self.installation_dir / self.source_and_target.target

    @property
    def source_plain(self) -> Path:
        return self.source_and_target.source

    @property
    def target_plain(self) -> Path:
        return self.installation_sub_dir / self.source_and_target.target


def _msg(msg: str):
    sys.stderr.write(msg + os.linesep)


class Make:
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

    def make_sub_dir(self,
                     base_dir: Path,
                     installation_sub_dir: str,
                     setups: Iterable[SourceAndTarget]):
        for setup in setups:
            self.make(SourceAndTargetSetup(base_dir, installation_sub_dir, setup))

    def make_all(self,
                 base_dir: Path,
                 sub_dir_configs: List[Tuple[str, Iterable[SourceAndTarget]]]):
        for sub_dir_config in sub_dir_configs:
            self.make_sub_dir(base_dir, sub_dir_config[0], sub_dir_config[1])

    def clean(self,
              setup: SourceAndTargetSetup):
        if setup.target.exists():
            _msg('Removing: ' + str(setup.target_plain))
            setup.target.unlink()

    def clean_sub_dir(self,
                      base_dir: Path,
                      installation_sub_dir: str,
                      setups: Iterable[SourceAndTarget]):
        for setup in setups:
            self.clean(SourceAndTargetSetup(base_dir, installation_sub_dir, setup))

    def clean_all(self,
                  base_dir: Path,
                  sub_dir_configs: List[Tuple[str, Iterable[SourceAndTarget]]]):
        for sub_dir_config in sub_dir_configs:
            self.clean_sub_dir(base_dir, sub_dir_config[0], sub_dir_config[1])

    def _is_fresh(self, setup: SourceAndTargetSetup):
        source_file = self._source_file(setup)
        ret_val = setup.target.is_file() and \
                  setup.target.stat().st_mtime >= source_file.stat().st_mtime
        if ret_val:
            _msg('Fresh : ' + str(setup.target_plain))
        return ret_val

    def _source_file(self, setup: SourceAndTargetSetup) -> Path:
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
    def _make_executable(target: Path):
        current_mode = target.stat().st_mode
        target.chmod(current_mode | stat.S_IEXEC)

    @staticmethod
    def _append_source(target_file, source: Path):
        target_file.write(source.open().read())


def _resolve_root(script_file_path_name: str) -> Path:
    script_file_path = Path(script_file_path_name)
    return script_file_path.resolve().parent


def main(sub_dir_configs: List[Tuple[str, Iterable[SourceAndTarget]]]):
    base_dir = _resolve_root(sys.argv[0])
    if not base_dir.is_dir():
        _msg('Cannot resolve root directory: ' + str(base_dir))
    _msg('Examples dir: ' + str(base_dir))
    if len(sys.argv) != 2:
        _msg("Usage all|clean")
        sys.exit(1)
    cmd = sys.argv[1]
    maker = Make('.py', sys.executable)
    if cmd == 'all':
        maker.make_all(base_dir, sub_dir_configs)
    elif cmd == 'clean':
        maker.clean_all(base_dir, sub_dir_configs)
    else:
        _msg('Not a command: ' + cmd)
        _msg("Usage all|clean")
        sys.exit(1)
