import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.util.file_utils import resolved_path


@contextmanager
def home_directory_structure(prefix: str = program_info.PROGRAM_NAME + '-test-hds-') \
        -> HomeDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=prefix) as case_dir_name:
        hds = HomeDirectoryStructure(resolved_path(case_dir_name))
        yield hds
