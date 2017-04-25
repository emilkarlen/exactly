import os
import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds_module
from exactly_lib.util.file_utils import resolved_path_name, preserved_cwd
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
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
