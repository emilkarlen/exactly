import os
from contextlib import contextmanager
from time import strftime, localtime
from typing import ContextManager

from exactly_lib import program_info
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators, sds_populator, non_hds_populator, \
    tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.ds_action import PlainTcdsAction
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import sandbox_directory_structure


@contextmanager
def tcds_with_act_as_curr_dir_2(
        hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
        sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
        non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
        tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
        pre_contents_population_action: PlainTcdsAction = PlainTcdsAction(),
) -> ContextManager[Tcds]:
    prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
    with home_directory_structure(prefix=prefix + '-home') as hds:
        with sandbox_directory_structure(prefix=prefix + "-sds-") as sds:
            tcds = Tcds(hds, sds)
            with preserved_cwd():
                os.chdir(str(sds.act_dir))
                pre_contents_population_action.apply(tcds)
                hds_contents.populate_hds(hds)
                sds_contents.populate_sds(sds)
                non_hds_contents.populate_non_hds(sds)
                tcds_contents.populate_tcds(tcds)
                yield tcds
