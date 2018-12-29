from typing import Callable

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.test_case.test_resources.arrangements import ActResultProducer


class ActResultProducerFromHomeAndSds2Str(ActResultProducer):
    def __init__(self, home_and_sds_2_str: Callable[[HomeAndSds], str]):
        self.home_and_sds_2_str = home_and_sds_2_str
