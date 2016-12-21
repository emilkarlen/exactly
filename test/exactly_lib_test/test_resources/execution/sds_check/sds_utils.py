import os
import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.test_case import sandbox_directory_structure as sds_module
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import resolved_path_name, preserved_cwd
from exactly_lib_test.test_resources.execution.sds_check import sds_populator


class SdsAction:
    def apply(self, sds: SandboxDirectoryStructure):
        pass


@contextmanager
def sds_with_act_as_curr_dir(contents: sds_populator.SdsPopulator = sds_populator.empty(),
                             pre_contents_population_action: SdsAction = SdsAction(),
                             ) -> sds_module.SandboxDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-sds-') as sds_root_dir:
        sds = sds_module.construct_at(resolved_path_name(sds_root_dir))
        with preserved_cwd():
            os.chdir(str(sds.act_dir))
            pre_contents_population_action.apply(sds)
            contents.apply(sds)
            yield sds


@contextmanager
def sandbox_directory_structure(contents: sds_populator.SdsPopulator = sds_populator.empty(),
                                prefix: str = program_info.PROGRAM_NAME + '-test-sds-') \
        -> sds_module.SandboxDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=prefix) as sds_root_dir:
        sds = sds_module.construct_at(resolved_path_name(sds_root_dir))
        contents.apply(sds)
        yield sds
