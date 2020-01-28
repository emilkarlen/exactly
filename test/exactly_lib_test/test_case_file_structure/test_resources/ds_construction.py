import os
from contextlib import contextmanager
from time import strftime, localtime
from typing import ContextManager, Optional

from exactly_lib import program_info
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib.util.functional import reduce_optional
from exactly_lib_test.test_case.test_resources.act_result import ActEnvironment, ActResultProducer, \
    ActResultProducerFromActResult, NULL_ACT_RESULT_PRODUCER
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators, sds_populator, non_hds_populator, \
    tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.ds_action import PlainTcdsAction
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import sandbox_directory_structure, \
    write_act_result


class TcdsArrangement:
    def __init__(self,
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 act_result: Optional[ActResultProducer] = None,
                 pre_population_action: PlainTcdsAction = PlainTcdsAction(),
                 post_population_action: PlainTcdsAction = PlainTcdsAction(),
                 ):
        self.hds_contents = hds_contents
        self.non_hds_contents = non_hds_contents
        self.tcds_contents = tcds_contents
        self.act_result = act_result
        self.pre_population_action = pre_population_action
        self.post_population_action = post_population_action


class TcdsArrangementPostAct:
    def __init__(self,
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 act_result: ActResultProducer = ActResultProducerFromActResult(),
                 pre_population_action: PlainTcdsAction = PlainTcdsAction(),
                 post_population_action: PlainTcdsAction = PlainTcdsAction(),
                 ):
        self.hds_contents = hds_contents
        self.non_hds_contents = non_hds_contents
        self.tcds_contents = tcds_contents
        self.act_result = act_result
        self.pre_population_action = pre_population_action
        self.post_population_action = post_population_action

    @staticmethod
    def of_tcds(a: TcdsArrangement) -> 'TcdsArrangementPostAct':
        return TcdsArrangementPostAct(
            tcds_contents=a.tcds_contents,
            hds_contents=a.hds_contents,
            non_hds_contents=a.non_hds_contents,
            act_result=reduce_optional(lambda x: x, NULL_ACT_RESULT_PRODUCER, a.act_result),
            pre_population_action=a.pre_population_action,
            post_population_action=a.post_population_action,
        )


def tcds_with_act_as_curr_dir_3(arrangement: TcdsArrangement) -> ContextManager[Tcds]:
    return tcds_with_act_as_curr_dir_2(
        hds_contents=arrangement.hds_contents,
        non_hds_contents=arrangement.non_hds_contents,
        tcds_contents=arrangement.tcds_contents,
        act_result=arrangement.act_result,
        pre_contents_population_action=arrangement.pre_population_action,
        post_contents_population_action=arrangement.post_population_action,
    )


def tcds_with_act_as_curr_dir__post_act(arrangement: TcdsArrangementPostAct) -> ContextManager[Tcds]:
    return tcds_with_act_as_curr_dir_2(
        hds_contents=arrangement.hds_contents,
        non_hds_contents=arrangement.non_hds_contents,
        tcds_contents=arrangement.tcds_contents,
        act_result=arrangement.act_result,
        pre_contents_population_action=arrangement.pre_population_action,
        post_contents_population_action=arrangement.post_population_action,
    )


@contextmanager
def tcds_with_act_as_curr_dir_2(
        hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
        sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
        non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
        tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
        act_result: Optional[ActResultProducer] = None,
        pre_contents_population_action: PlainTcdsAction = PlainTcdsAction(),
        post_contents_population_action: PlainTcdsAction = PlainTcdsAction(),
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
                if act_result:
                    actual_act_result = act_result.apply(ActEnvironment(tcds))
                    write_act_result(tcds.sds, actual_act_result)
                post_contents_population_action.apply(tcds)
                yield tcds
