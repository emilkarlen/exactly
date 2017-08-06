import os
import pathlib
import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds_module
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import resolved_path_name, preserved_cwd
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator


class SdsAction:
    def apply(self, environment: PathResolvingEnvironmentPostSds):
        pass


@contextmanager
def sds_with_act_as_curr_dir(contents: sds_populator.SdsPopulator = sds_populator.empty(),
                             pre_contents_population_action: SdsAction = SdsAction(),
                             symbols: SymbolTable = None,
                             ) -> PathResolvingEnvironmentPostSds:
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-sds-') as sds_root_dir:
        sds = sds_module.construct_at(resolved_path_name(sds_root_dir))
        environment = PathResolvingEnvironmentPostSds(sds, symbol_table_from_none_or_value(symbols))
        with preserved_cwd():
            os.chdir(str(sds.act_dir))
            pre_contents_population_action.apply(environment)
            contents.populate_sds(sds)
            yield environment


class MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs(SdsAction):
    DIR_NAME = 'not-a-std-sub-dir-of-sds'

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        dir_path = self.resolve_dir_path(environment.sds)
        dir_path.mkdir(parents=True, exist_ok=True)
        os.chdir(str(dir_path))

    def resolve_dir_path(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.root_dir / self.DIR_NAME
