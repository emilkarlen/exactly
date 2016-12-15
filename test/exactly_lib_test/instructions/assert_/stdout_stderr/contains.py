import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contains as test_resources
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestConfiguration
from exactly_lib_test.instructions.test_resources.arrangements import ActEnvironment, \
    ActResultProducerFromActResult
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.parse import new_source2


class _TestConfigurationForStdFile(TestConfiguration):
    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        return new_source2(argument_tail)

    def arrangement_for_contents(self, actual_contents: str) -> instruction_check.ArrangementPostAct:
        act_result = self.act_result(actual_contents)
        act_result_producer = ActResultProducerFromActResult(act_result)
        return instruction_check.ArrangementPostAct(act_result_producer=act_result_producer)

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        raise NotImplementedError()


class _ActResultProducerForStdout(test_resources.ActResultProducerFromHomeAndSds2Str):
    def apply(self, act_environment: ActEnvironment) -> ActResult:
        return ActResult(stdout_contents=self.home_and_sds_2_str(act_environment.home_and_sds))


class _ActResultProducerForStderr(test_resources.ActResultProducerFromHomeAndSds2Str):
    def apply(self, act_environment: ActEnvironment) -> ActResult:
        return ActResult(stderr_contents=self.home_and_sds_2_str(act_environment.home_and_sds))


class _TestConfigurationForStdout(_TestConfigurationForStdFile):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(act_result_producer=_ActResultProducerForStdout(home_and_sds_2_str))

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        return ActResult(stdout_contents=contents_of_tested_file)


class _TestConfigurationForStderr(_TestConfigurationForStdFile):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(act_result_producer=_ActResultProducerForStderr(home_and_sds_2_str))

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        return ActResult(stderr_contents=contents_of_tested_file)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources.suite_for(_TestConfigurationForStdout()),
        test_resources.suite_for(_TestConfigurationForStderr()),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
