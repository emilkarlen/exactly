from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib_test.test_resources.process import SubProcessResult


class ActEnvironment(tuple):
    def __new__(cls,
                tcds: TestCaseDs):
        return tuple.__new__(cls, (tcds,))

    @property
    def tcds(self) -> TestCaseDs:
        return self[0]


class ActResultProducer:
    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        raise NotImplementedError()


class ActResultProducerFromActResult(ActResultProducer):
    def __init__(self, act_result: SubProcessResult = SubProcessResult()):
        self.act_result = act_result

    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        return self.act_result


NULL_ACT_RESULT_PRODUCER = ActResultProducerFromActResult()
