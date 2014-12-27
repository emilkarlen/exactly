__author__ = 'karlen'


from pathlib import Path


class DirWithSubDirs:
    def __init__(self, name: str,
                 sub_dirs: list):
        self.name = name
        self.sub_dirs = sub_dirs

    def mk_dirs(self, existing_root_dir: Path):
        this_dir = existing_root_dir / self.name
        this_dir.mkdir()
        for sub_dir in self.sub_dirs:
            sub_dir.mk_dirs(this_dir)


execution_directories = [
    DirWithSubDirs('result',
                   [DirWithSubDirs('std', [])]),
    DirWithSubDirs('test', []),
    DirWithSubDirs('testcase', []),
    DirWithSubDirs('log', []),
]


def construct_execution_directory_structure(execution_directory_root: str):
    for d in execution_directories:
        d.mk_dirs(Path(Path(execution_directory_root)))
