import os
import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds_module
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import resolved_path_name, preserved_cwd
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.file_utils import write_file
from exactly_lib_test.util.test_resources.symbol_table import symbol_table_from_none_or_value


class SdsAction:
    def apply(self, environment: PathResolvingEnvironmentPostSds):
        pass


@contextmanager
def sds_with_act_as_curr_dir(contents: sds_populator.SdsPopulator = sds_populator.empty(),
                             pre_contents_population_action: SdsAction = SdsAction(),
                             value_definitions: SymbolTable = None,
                             ) -> PathResolvingEnvironmentPostSds:
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-sds-') as sds_root_dir:
        sds = sds_module.construct_at(resolved_path_name(sds_root_dir))
        environment = PathResolvingEnvironmentPostSds(sds, symbol_table_from_none_or_value(value_definitions))
        with preserved_cwd():
            os.chdir(str(sds.act_dir))
            pre_contents_population_action.apply(environment)
            contents.apply(sds)
            yield environment


@contextmanager
def sandbox_directory_structure(contents: sds_populator.SdsPopulator = sds_populator.empty(),
                                prefix: str = program_info.PROGRAM_NAME + '-test-sds-') \
        -> sds_module.SandboxDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=prefix) as sds_root_dir:
        sds = sds_module.construct_at(resolved_path_name(sds_root_dir))
        contents.apply(sds)
        yield sds


def write_act_result(sds: SandboxDirectoryStructure,
                     result: ActResult):
    write_file(sds.result.exitcode_file, str(result.exitcode))
    write_file(sds.result.stdout_file, result.stdout_contents)
    write_file(sds.result.stderr_file, result.stderr_contents)


class MkDirIfNotExistsAndChangeToIt(SdsAction):
    def __init__(self, sds_2_dir_path):
        self.sds_2_dir_path = sds_2_dir_path

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        dir_path = self.sds_2_dir_path(environment.sds)
        dir_path.mkdir(parents=True, exist_ok=True)
        os.chdir(str(dir_path))


def mk_sub_dir_of_act_and_change_to_it(sub_dir_name: str) -> SdsAction:
    return MkDirIfNotExistsAndChangeToIt(lambda sds: sds.act_dir / sub_dir_name)
