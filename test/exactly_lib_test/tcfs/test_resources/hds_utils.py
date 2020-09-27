import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.util.file_utils.misc_utils import resolved_path
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.tcfs.test_resources.dir_populator import HdsPopulator


@contextmanager
def home_directory_structure(contents: HdsPopulator = hds_populators.empty(),
                             prefix: str = program_info.PROGRAM_NAME + '-test-hds-') \
        -> HomeDs:
    with tempfile.TemporaryDirectory(prefix=prefix + '-case') as case_dir_name:
        with tempfile.TemporaryDirectory(prefix=prefix + '-act') as act_dir_name:
            hds = HomeDs(case_dir=resolved_path(case_dir_name),
                         act_dir=resolved_path(act_dir_name))
            contents.populate_hds(hds)
            yield hds
