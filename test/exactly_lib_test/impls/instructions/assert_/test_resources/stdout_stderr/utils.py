from typing import Callable

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducer


class ActResultProducerFromTcds2Str(ActResultProducer):
    def __init__(self, tcds_2_str: Callable[[TestCaseDs], str]):
        self.tcds_2_str = tcds_2_str
