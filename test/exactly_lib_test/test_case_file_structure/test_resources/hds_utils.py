import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.util.file_utils import resolved_path
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomePopulator


@contextmanager
def home_directory_structure(contents: HomePopulator = home_populators.empty(),
                             prefix: str = program_info.PROGRAM_NAME + '-test-hds-') \
        -> HomeDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=prefix + '-case') as case_dir_name:
        with tempfile.TemporaryDirectory(prefix=prefix + '-act') as act_dir_name:
            hds = HomeDirectoryStructure(case_dir=resolved_path(case_dir_name),
                                         act_dir=resolved_path(act_dir_name))
            contents.populate_hds(hds)
            yield hds
