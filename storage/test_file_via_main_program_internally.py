import unittest

from exactly_lib.common.instruction_name_and_argument_splitter import splitter
from exactly_lib_test.cli_default.test_resources.internal_main_program_runner import RunViaMainProgramInternally

TEST_CASE_FILE = '../tmp/error-source-file-location/sub1/the.case'


class TC(unittest.TestCase):
    def test(self):
        runner = RunViaMainProgramInternally(name_and_argument_splitter=splitter)
        result = runner.run(self, [TEST_CASE_FILE])
        print('EXIT CODE: ' + str(result.exitcode))
        print('STDOUT:\n' + str(result.stdout))
        print('STDERR:\n' + str(result.stderr))
