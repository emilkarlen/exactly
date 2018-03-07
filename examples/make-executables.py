import itertools
import os
import pathlib
import stat
import sys
from typing import List, Tuple


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
                installation_sub_dir: str,
                source_and_target: SourceAndTarget):
        return tuple.__new__(cls, (base_dir,
                                   pathlib.Path(installation_sub_dir),
                                   source_and_target))

    @property
    def base_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def installation_sub_dir(self) -> pathlib.Path:
        return self[1]

    @property
    def installation_dir(self) -> pathlib.Path:
        return self.base_dir / self.installation_sub_dir

    @property
    def source_and_target(self) -> SourceAndTarget:
        return self[2]

    @property
    def source(self) -> pathlib.Path:
        return self.base_dir / self.source_and_target.source

    @property
    def target(self) -> pathlib.Path:
        return self.installation_dir / self.source_and_target.target

    @property
    def source_plain(self) -> pathlib.Path:
        return self.source_and_target.source

    @property
    def target_plain(self) -> pathlib.Path:
        return self.installation_sub_dir / self.source_and_target.target


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

    def make_sub_dir(self,
                     base_dir: pathlib.Path,
                     installation_sub_dir: str,
                     setups: List[SourceAndTarget]):
        for setup in setups:
            self.make(SourceAndTargetSetup(base_dir, installation_sub_dir, setup))

    def make_all(self,
                 base_dir: pathlib.Path,
                 sub_dir_configs: List[Tuple[str, List[SourceAndTarget]]]):
        for sub_dir_config in sub_dir_configs:
            self.make_sub_dir(base_dir, sub_dir_config[0], sub_dir_config[1])

    def clean(self,
              setup: SourceAndTargetSetup):
        if setup.target.exists():
            _msg('Removing: ' + str(setup.target_plain))
            setup.target.unlink()

    def clean_sub_dir(self,
                      base_dir: pathlib.Path,
                      installation_sub_dir: str,
                      setups: List[SourceAndTarget]):
        for setup in setups:
            self.clean(SourceAndTargetSetup(base_dir, installation_sub_dir, setup))

    def clean_all(self,
                  base_dir: pathlib.Path,
                  sub_dir_configs: List[Tuple[str, List[SourceAndTarget]]]):
        for sub_dir_config in sub_dir_configs:
            self.clean_sub_dir(base_dir, sub_dir_config[0], sub_dir_config[1])

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


intro_sub_dir = 'intro'
wiki_sub_dir = 'wiki'

wiki_hello_world_dir = pathlib.Path('hello-world')

src_base_dir = pathlib.Path('executables-src')
first_step_dir = pathlib.Path('first-step')
sandbox_dir = pathlib.Path('sandbox-directories')
symbols_dir = pathlib.Path('symbols')
home_dir = pathlib.Path('home-directories')
cleanup_dir = pathlib.Path('cleanup')
dir_contents_dir = pathlib.Path('dir-contents')
external_programs_dir = pathlib.Path('external-programs')
setup_dir = pathlib.Path('setup')
file_transformations_dir = pathlib.Path('file-transformations')

readme_examples_root_dir = 'readme-file-examples'

readme_contacts_dir = pathlib.Path('contacts')
readme_classify_dir = pathlib.Path('classify')


def st(target_base: pathlib.Path, file_name: str) -> SourceAndTarget:
    return SourceAndTarget(src_base_dir / file_name,
                           target_base / file_name)


def sts(target_base: pathlib.Path, file_names: List[str]) -> List[SourceAndTarget]:
    return [st(target_base, file_name) for file_name in file_names]


def do_nothing(target_file: pathlib.Path) -> SourceAndTarget:
    return SourceAndTarget(src_base_dir / 'do-nothing',
                           target_file)


def do_nothing_list(target_base: pathlib.Path, target_file_names: list) -> list:
    return [do_nothing(target_base / file_name) for file_name in target_file_names]


readme_files = itertools.chain.from_iterable([
    sts(readme_contacts_dir,
        ['my-contacts-program',
         ]),
    sts(readme_classify_dir,
        ['classify-files-by-moving-to-appropriate-dir',
         ]),
])

intro_files = itertools.chain.from_iterable(
    [
        sts(first_step_dir,
            ['hello-world',
             'filter-lines',
             ]),

        sts(sandbox_dir,
            ['hello-world',
             'classify-files-by-moving-to-appropriate-dir',
             'remove-all-files-in-the-current-directory',
             ]),

        sts(symbols_dir / 'bin',
            ['print-number-of-arguments',
             'print-one-argument-per-line',
             'classify-files-by-moving-to-appropriate-dir',
             'print-number-of-lines-in-file',
             'filter-lines',
             ]),

        sts(file_transformations_dir / 'bin',
            ['print-one-argument-per-line',
             ]),

        do_nothing_list(cleanup_dir,
                        ['manipulate-database-contents',
                         'my-helper-program',
                         ]),

        do_nothing_list(external_programs_dir,
                        ['my-assert-helper-program',
                         'my-setup-helper-program',
                         'system-under-test',
                         ]),

        do_nothing_list(home_dir / 'bin',
                        ['do-something-good-with',
                         ]),

        sts(setup_dir,
            ['copy-stdin-to-stdout',
             'remove-all-files-in-the-current-directory',
             'print-environment-variables',
             'list-files-under-current-directory',
             ]),
    ])

wiki_files = itertools.chain.from_iterable(
    [
        sts(wiki_hello_world_dir,
            ['hello-world',
             ]),

    ])

sub_dir_configs = [
    (intro_sub_dir, intro_files),
    (readme_examples_root_dir, readme_files),
    (wiki_sub_dir, wiki_files),
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
        maker.make_all(base_dir, sub_dir_configs)
    elif cmd == 'clean':
        maker.clean_all(base_dir, sub_dir_configs)
    else:
        _msg('Not a command: ' + cmd)
        sys.exit(1)
