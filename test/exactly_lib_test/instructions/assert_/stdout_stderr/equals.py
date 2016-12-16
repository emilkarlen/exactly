import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.instructions.assert_.utils.file_contents.parsing import EQUALS_ARGUMENT
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestWithParserBase, \
    TestConfigurationForStdout, TestConfigurationForStderr
from exactly_lib_test.instructions.assert_.test_resources.file_contents import equals
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducerFromActResult
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.parse import argument_list_source


class FileContentsHereDoc(TestWithParserBase):
    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        raise NotImplementedError()

    def pass__when__contents_equals(self):
        self._run(
            argument_list_source([EQUALS_ARGUMENT, '<<EOF'],
                                 ['single line',
                                  'EOF']),
            arrangement(act_result_producer=ActResultProducerFromActResult(
                self._act_result_with_contents(lines_content(['single line'])))),
            is_pass(),
        )


class FileContentsHereDocFORStdout(FileContentsHereDoc):
    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stdout_contents=contents_on_tested_channel,
                         stderr_contents=contents_on_other_channel)


class FileContentsHereDocFORStderr(FileContentsHereDoc):
    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stderr_contents=contents_on_tested_channel,
                         stdout_contents=contents_on_other_channel)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(FileContentsHereDocFORStdout),
        unittest.makeSuite(FileContentsHereDocFORStderr),

        equals.suite_for(TestConfigurationForStdout()),
        equals.suite_for(TestConfigurationForStderr()),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
