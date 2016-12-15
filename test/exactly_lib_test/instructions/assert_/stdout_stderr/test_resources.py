from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contains as test_resources
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ActEnvironment, \
    ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulator
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.parse import new_source2


class TestWithParserBase(instruction_check.TestCaseBase):
    def _new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        self._check(self._new_parser(), source, arrangement, expectation)


class TestConfigurationForStdFile(TestConfiguration):
    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        return new_source2(argument_tail)

    def arrangement_for_contents(self, actual_contents: str) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=(self._act_result_producer(actual_contents))
        )

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=(self._act_result_producer(actual_contents)),
            home_or_sds_contents=expected
        )

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        raise NotImplementedError()

    def _act_result_producer(self, contents_of_tested_file: str) -> instruction_check.ActResultProducer:
        act_result = self.act_result(contents_of_tested_file)
        return ActResultProducerFromActResult(act_result)


class ActResultProducerForStdout(test_resources.ActResultProducerFromHomeAndSds2Str):
    def apply(self, act_environment: ActEnvironment) -> ActResult:
        return ActResult(stdout_contents=self.home_and_sds_2_str(act_environment.home_and_sds))


class ActResultProducerForStderr(test_resources.ActResultProducerFromHomeAndSds2Str):
    def apply(self, act_environment: ActEnvironment) -> ActResult:
        return ActResult(stderr_contents=self.home_and_sds_2_str(act_environment.home_and_sds))


class TestConfigurationForStdout(TestConfigurationForStdFile):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(act_result_producer=ActResultProducerForStdout(home_and_sds_2_str))

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        return ActResult(stdout_contents=contents_of_tested_file)


class TestConfigurationForStderr(TestConfigurationForStdFile):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(act_result_producer=ActResultProducerForStderr(home_and_sds_2_str))

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        return ActResult(stderr_contents=contents_of_tested_file)
