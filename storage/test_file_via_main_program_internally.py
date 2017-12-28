import unittest

from exactly_lib.default.instruction_name_and_argument_splitter import splitter
from exactly_lib_test.default.test_resources.internal_main_program_runner import RunViaMainProgramInternally

TEST_CASE_FILE = '/Users/emil/vcs/exactly/0/err_msg_tests/symbol-validation/path-dir-component-contains-path-ref--indirect-ref--def.case'


class TC(unittest.TestCase):
    def test(self):
        runner = RunViaMainProgramInternally(name_and_argument_splitter=splitter)
        result = runner.run(self, [TEST_CASE_FILE])
        print(str(result))
