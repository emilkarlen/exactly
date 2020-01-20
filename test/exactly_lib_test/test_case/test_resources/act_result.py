from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib_test.test_resources.process import SubProcessResult


class ActEnvironment(tuple):
    def __new__(cls,
                tcds: Tcds):
        return tuple.__new__(cls, (tcds,))

    @property
    def tcds(self) -> Tcds:
        return self[0]


class ActResultProducer:
    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        raise NotImplementedError()


class ActResultProducerFromActResult(ActResultProducer):
    def __init__(self, act_result: SubProcessResult = SubProcessResult()):
        self.act_result = act_result

    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        return self.act_result
