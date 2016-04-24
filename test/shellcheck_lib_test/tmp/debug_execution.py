import unittest

from shellcheck_lib.default.default_main_program_setup import *


class TestCase(unittest.TestCase):
    def test(self):
        exit_status = default_main_program().execute(['--actor',
                                                      '/usr/bin/python3',
                                                      '/home/karlen/vcs/shellcheck/github/tmp/bug.case'])
        print(exit_status)
