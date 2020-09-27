import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.tcfs import sds as sds_module
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.util.file_utils.misc_utils import resolved_path_name
from exactly_lib_test.tcfs.test_resources import sds_populator
from exactly_lib_test.test_resources.files.file_utils import write_file
from exactly_lib_test.test_resources.process import SubProcessResult


@contextmanager
def sandbox_directory_structure(contents: sds_populator.SdsPopulator = sds_populator.empty(),
                                prefix: str = program_info.PROGRAM_NAME + '-test-sds-') \
        -> sds_module.SandboxDs:
    with tempfile.TemporaryDirectory(prefix=prefix) as sds_root_dir:
        sds = sds_module.construct_at(resolved_path_name(sds_root_dir))
        contents.populate_sds(sds)
        yield sds


def write_act_result(sds: SandboxDs,
                     result: SubProcessResult):
    write_file(sds.result.exitcode_file, str(result.exitcode))
    write_file(sds.result.stdout_file, result.stdout)
    write_file(sds.result.stderr_file, result.stderr)
