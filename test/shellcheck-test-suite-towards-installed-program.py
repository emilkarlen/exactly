import unittest

import shellcheck_lib_test
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.main_program_runner import \
    RunInstalledProgramViaOsInSubProcess

import test_cli_main_program__test_case
import test_cli_main_program__invalid_invokation_dynamic
import test_cli_main_program__test_suite

# This value is from setup.py
EXECUTABLE_NAME = 'shellcheck'

main_program_runner = RunInstalledProgramViaOsInSubProcess(EXECUTABLE_NAME)
suite = unittest.TestSuite()
suite.addTest(shellcheck_lib_test.suite())
suite.addTest(test_cli_main_program__test_case.suite_for(main_program_runner))
suite.addTest(test_cli_main_program__invalid_invokation_dynamic.suite_for(main_program_runner))
# suite.addTest(test_cli_main_program__test_suite.suite())

runner = unittest.TextTestRunner()
runner.run(suite)
