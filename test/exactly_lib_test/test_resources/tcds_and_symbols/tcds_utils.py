import os
from contextlib import contextmanager
from time import strftime, localtime
from typing import ContextManager, Optional

from exactly_lib import program_info
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.tcfs.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.tcfs.test_resources.ds_action import PlainTcdsAction
from exactly_lib_test.tcfs.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.tcfs.test_resources.sds_check.sds_utils import sandbox_directory_structure
from exactly_lib_test.test_resources.tcds_and_symbols.sds_env_utils import SdsAction, \
    mk_dir_and_change_to_it_inside_of_sds_but_outside_of_any_of_the_relativity_option_dirs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def sds_2_tcds_assertion(assertion_on_sds: Assertion[SandboxDs]
                         ) -> Assertion[TestCaseDs]:
    return asrt.sub_component('sds',
                              TestCaseDs.sds.fget,
                              assertion_on_sds)


class TcdsAction:
    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        pass


class TcdsActionFromSdsAction(TcdsAction):
    def __init__(self, sds_action: SdsAction):
        self.sds_action = sds_action

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        return self.sds_action.apply(environment)


class TcdsActionFromPlainTcdsAction(TcdsAction):
    def __init__(self, plain_action: PlainTcdsAction):
        self.plain_action = plain_action

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        return self.plain_action.apply(environment.tcds)


class PlainTcdsActionFromTcdsAction(PlainTcdsAction):
    def __init__(self,
                 action: TcdsAction,
                 symbols: Optional[SymbolTable] = None,
                 ):
        self.symbols = symbols
        self.action = action

    def apply(self, tcds: TestCaseDs):
        environment = PathResolvingEnvironmentPreOrPostSds(tcds, self.symbols)
        return self.action.apply(environment)


@contextmanager
def tcds_with_act_as_curr_dir(
        hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
        sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
        non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
        tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
        pre_contents_population_action: TcdsAction = TcdsAction(),
        symbols: SymbolTable = None) -> ContextManager[PathResolvingEnvironmentPreOrPostSds]:
    symbols = symbol_table_from_none_or_value(symbols)
    prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
    with home_directory_structure(prefix=prefix + '-home') as hds:
        with sandbox_directory_structure(prefix=prefix + "-sds-") as sds:
            tcds = TestCaseDs(hds, sds)
            ret_val = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)
            with preserved_cwd():
                os.chdir(str(sds.act_dir))
                pre_contents_population_action.apply(ret_val)
                hds_contents.populate_hds(hds)
                sds_contents.populate_sds(sds)
                non_hds_contents.populate_non_hds(sds)
                tcds_contents.populate_tcds(tcds)
                yield ret_val


SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR__PLAIN = (
    mk_dir_and_change_to_it_inside_of_sds_but_outside_of_any_of_the_relativity_option_dirs()
)

SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR = TcdsActionFromSdsAction(
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR__PLAIN
)
