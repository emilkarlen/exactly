import os
import tempfile
from contextlib import contextmanager

from exactly_lib import program_info
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.tcfs import sds as sds_module
from exactly_lib.util.file_utils.misc_utils import resolved_path_name, preserved_cwd
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.tcfs.test_resources import sds_populator
from exactly_lib_test.tcfs.test_resources.ds_action import \
    MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs, PlainSdsAction


class SdsAction:
    def apply(self, environment: PathResolvingEnvironmentPostSds):
        pass


class SdsActionFromPlainSdsAction(SdsAction):
    def __init__(self, plain_action: PlainSdsAction):
        self._plain_action = plain_action

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        self._plain_action.apply(environment.sds)


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


def mk_dir_and_change_to_it_inside_of_sds_but_outside_of_any_of_the_relativity_option_dirs() -> SdsAction:
    return SdsActionFromPlainSdsAction(
        MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs()
    )
