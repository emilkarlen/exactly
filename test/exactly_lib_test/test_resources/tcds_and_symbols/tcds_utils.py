import os
from contextlib import contextmanager
from time import strftime, localtime
from typing import ContextManager

from exactly_lib import program_info
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import sandbox_directory_structure
from exactly_lib_test.test_resources.tcds_and_symbols.sds_env_utils import SdsAction, \
    MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def sds_2_tcds_assertion(assertion_on_sds: ValueAssertion[SandboxDirectoryStructure]
                         ) -> ValueAssertion[Tcds]:
    return asrt.sub_component('sds',
                              Tcds.sds.fget,
                              assertion_on_sds)


class HdsAndSdsAction:
    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        pass


class HdsAndSdsActionFromSdsAction(HdsAndSdsAction):
    def __init__(self, sds_action: SdsAction):
        self.sds_action = sds_action

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        return self.sds_action.apply(environment)


@contextmanager
def tcds_with_act_as_curr_dir(
        hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
        sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
        non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
        tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
        pre_contents_population_action: HdsAndSdsAction = HdsAndSdsAction(),
        symbols: SymbolTable = None) -> ContextManager[PathResolvingEnvironmentPreOrPostSds]:
    symbols = symbol_table_from_none_or_value(symbols)
    prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
    with home_directory_structure(prefix=prefix + '-home') as hds:
        with sandbox_directory_structure(prefix=prefix + "-sds-") as sds:
            tcds = Tcds(hds, sds)
            ret_val = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)
            with preserved_cwd():
                os.chdir(str(sds.act_dir))
                pre_contents_population_action.apply(ret_val)
                hds_contents.populate_hds(hds)
                sds_contents.populate_sds(sds)
                non_hds_contents.populate_non_hds(sds)
                tcds_contents.populate_tcds(tcds)
                yield ret_val


SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR = HdsAndSdsActionFromSdsAction(
    MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs())
