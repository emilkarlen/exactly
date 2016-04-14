import os
import sys
import unittest

import shellcheck_lib_test
from shellcheck_lib_test.test_resources.main_program.main_program_runner import RunViaOsInSubProcess

SRC_DIR_NAME = 'src'

this_dir = sys.path[0]
prj_root_dir = os.path.dirname(this_dir)
src_dir = os.path.join(prj_root_dir, SRC_DIR_NAME)
sys.path.insert(0, src_dir)

os.chdir(this_dir)

import test_cli_main_program__test_case
import test_cli_main_program__invalid_invokation_dynamic
import test_cli_main_program__test_suite

main_program_runner = RunViaOsInSubProcess()
suite = unittest.TestSuite()
suite.addTest(shellcheck_lib_test.suite())
suite.addTest(test_cli_main_program__test_case.suite())
suite.addTest(test_cli_main_program__invalid_invokation_dynamic.suite_for(main_program_runner))
suite.addTest(test_cli_main_program__test_suite.suite())

runner = unittest.TextTestRunner()
runner.run(suite)
