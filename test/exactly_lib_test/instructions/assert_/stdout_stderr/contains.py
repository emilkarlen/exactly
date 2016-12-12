import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.instructions.assert_.utils.file_contents.parsing import MATCHES_ARGUMENT
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ActResultProducer, \
    arrangement, Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class TestConfiguration:
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def act_result(self,
                   exit_code: int = 0,
                   contents_of_tested_file: str = '',
                   contents_of_other_file: str = '') -> ActResult:
        raise NotImplementedError()


class TestConfigurationForStdout(TestConfiguration):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def act_result(self,
                   exit_code: int = 0,
                   contents_of_tested_file: str = '',
                   contents_of_other_file: str = '') -> ActResult:
        return ActResult(exitcode=exit_code,
                         stdout_contents=contents_of_tested_file,
                         stderr_contents=contents_of_other_file)


class TestConfigurationForStderr(TestConfiguration):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def act_result(self,
                   exit_code: int = 0,
                   contents_of_tested_file: str = '',
                   contents_of_other_file: str = '') -> ActResult:
        return ActResult(exitcode=exit_code,
                         stderr_contents=contents_of_tested_file,
                         stdout_contents=contents_of_other_file)


class TestWithConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: TestConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               source: SingleInstructionParserSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)

    def _act_result_producer(self,
                             exit_code: int = 0,
                             contents_of_tested_file: str = '',
                             contents_of_other_file: str = '') -> ActResultProducer:
        act_result = self.configuration.act_result(exit_code=exit_code,
                                                   contents_of_tested_file=contents_of_tested_file,
                                                   contents_of_other_file=contents_of_other_file)
        return ActResultProducer(act_result)


class TestParseMatchesWithMissingRegExArgument(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(new_source2(MATCHES_ARGUMENT))


class TestParseMatchesWithSuperfluousArgument(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(new_source2('{} abc superfluous'.format(MATCHES_ARGUMENT)))


class TestParseMatchesWithInvalidRegEx(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(new_source2('{} **'.format(MATCHES_ARGUMENT)))


class TestMatchesShouldFailWhenNoLineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        act_result_producer = self._act_result_producer(contents_of_tested_file=actual_contents)
        reg_ex = '123'
        self._check(
            new_source2("%s '%s'" % (MATCHES_ARGUMENT, reg_ex)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestMatchesShouldPassWhenALineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        act_result_producer = self._act_result_producer(contents_of_tested_file=actual_contents)
        reg_ex = 'ATC'
        self._check(
            new_source2("%s '%s'" % (MATCHES_ARGUMENT, reg_ex)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_pass()),
        )


class TestMatchesShouldPassWhenAWholeLineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        act_result_producer = self._act_result_producer(contents_of_tested_file=actual_contents)
        reg_ex = '^MATCH$'
        self._check(
            new_source2("%s '%s'" % (MATCHES_ARGUMENT, reg_ex)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_pass()),
        )


def suite_for_matches(configuration: TestConfiguration) -> unittest.TestSuite:
    test_cases = [
        TestParseMatchesWithMissingRegExArgument,
        TestParseMatchesWithSuperfluousArgument,
        TestParseMatchesWithInvalidRegEx,
        TestMatchesShouldFailWhenNoLineMatchesRegEx,
        TestMatchesShouldPassWhenALineMatchesRegEx,
        TestMatchesShouldPassWhenAWholeLineMatchesRegEx,
    ]
    return unittest.TestSuite([tc(configuration) for tc in test_cases])


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_matches(TestConfigurationForStdout()),
        suite_for_matches(TestConfigurationForStderr()),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
