from typing import Callable

from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib_test.test_case.test_resources.arrangements import ActResultProducer


class ActResultProducerFromTcds2Str(ActResultProducer):
    def __init__(self, tcds_2_str: Callable[[Tcds], str]):
        self.tcds_2_str = tcds_2_str
