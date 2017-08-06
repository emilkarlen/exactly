import os
import tempfile
from contextlib import contextmanager
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.util.file_utils import resolved_path, preserved_cwd
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator, home_populators
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import sandbox_directory_structure
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.sds_env_utils import SdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.symbol_tables import symbol_table_from_none_or_value


def sds_2_home_and_sds_assertion(assertion_on_sds: asrt.ValueAssertion):
    return asrt.sub_component('sds',
                              HomeAndSds.sds.fget,
                              assertion_on_sds)


class HomeAndSdsAction:
    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        pass


class HomeAndSdsActionFromSdsAction(HomeAndSdsAction):
    def __init__(self, sds_action: SdsAction):
        self.sds_action = sds_action

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        return self.sds_action.apply(environment)


@contextmanager
def home_and_sds_with_act_as_curr_dir(
        hds_contents: home_populators.HomePopulator = home_populators.empty(),
        sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
        non_home_contents: non_home_populator.NonHomePopulator = non_home_populator.empty(),
        home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
        pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
        symbols: SymbolTable = None) -> PathResolvingEnvironmentPreOrPostSds:
    symbols = symbol_table_from_none_or_value(symbols)
    prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + '-home-case') as home_case_dir:
        with tempfile.TemporaryDirectory(prefix=prefix + '-home-act') as home_act_dir:
            home_case_dir_path = resolved_path(home_case_dir)
            home_act_dir_path = resolved_path(home_act_dir)
            with sandbox_directory_structure(prefix=prefix + "-sds-") as sds:
                hds = HomeDirectoryStructure(case_dir=home_case_dir_path,
                                             act_dir=home_act_dir_path)
                home_and_sds = HomeAndSds(hds, sds)
                ret_val = PathResolvingEnvironmentPreOrPostSds(home_and_sds, symbols)
                with preserved_cwd():
                    os.chdir(str(sds.act_dir))
                    pre_contents_population_action.apply(ret_val)
                    hds_contents.populate_hds(hds)
                    sds_contents.populate_sds(sds)
                    non_home_contents.populate_non_home(sds)
                    home_or_sds_contents.populate_home_or_sds(home_and_sds)
                    yield ret_val
