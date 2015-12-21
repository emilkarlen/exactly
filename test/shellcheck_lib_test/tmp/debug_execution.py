import unittest

from shellcheck_lib.default.default_main_program_setup import *


class TestCase(unittest.TestCase):
    def test(self):
        exit_status = default_main_program().execute(['/home/karlen/tmp/shellcheck/home-bugg/tc.testcase'])
        print(exit_status)
