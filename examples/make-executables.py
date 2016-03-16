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
            _msg('Fresh : ' + str(setup.target_plain))
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


src_base_dir = pathlib.Path('executables-src')
first_step_dir = pathlib.Path('first-step')
cleanup_dir = pathlib.Path('cleanup')
external_programs_dir = pathlib.Path('external-programs')
organize_dir = pathlib.Path('organize')
setup_dir = pathlib.Path('setup')


def st(target_base: pathlib.Path, file_name: str) -> SourceAndTarget:
    return SourceAndTarget(src_base_dir / file_name,
                           target_base / file_name)


st2 = SourceAndTarget


def do_nothing(target_file: pathlib.Path) -> SourceAndTarget:
    return st2(src_base_dir / 'do-nothing',
               target_file)


files = [
    st(first_step_dir, 'hello-world'),
    st(first_step_dir, 'remove-all-files-in-the-current-directory'),

    do_nothing(cleanup_dir / 'manipulate-database-contents'),
    do_nothing(cleanup_dir / 'my-helper-program'),

    do_nothing(external_programs_dir / 'my-assert-helper-program'),
    do_nothing(external_programs_dir / 'my-setup-helper-program'),
    do_nothing(external_programs_dir / 'system-under-test'),

    do_nothing(organize_dir / 'bin' / 'do-something-good-with'),

    st(setup_dir, 'copy-stdin-to-stdout'),
    st(setup_dir, 'remove-all-files-in-the-current-directory'),
    st(setup_dir, 'list-files-under-pwd'),
]

if __name__ == '__main__':
    base_dir = _resolve_root(sys.argv[0])
    if not base_dir.is_dir():
        _msg('Cannot resolve root directory: ' + str(base_dir))
    _msg('Examples dir: ' + str(base_dir))
    if len(sys.argv) != 2:
        _msg("Usage all|clean")
        sys.exit(1)
    cmd = sys.argv[1]
    maker = UnixMake('.py', sys.executable)
    if cmd == 'all':
        maker.make_all(base_dir, files)
    elif cmd == 'clean':
        maker.clean_all(base_dir, files)
    else:
        _msg('Unknown command: ' + cmd)
        sys.exit(1)
