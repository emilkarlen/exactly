import unittest

import shellcheck_lib_test
import test_cli_main_program__invalid_invokation_dynamic
import test_cli_main_program__test_case
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.main_program_runner import \
    RunInstalledProgramViaOsInSubProcess

# This value is from setup.py
EXECUTABLE_NAME = 'shellcheck'

main_program_runner = RunInstalledProgramViaOsInSubProcess(EXECUTABLE_NAME)
suite = unittest.TestSuite()
suite.addTest(shellcheck_lib_test.suite())
suite.addTest(test_cli_main_program__test_case.suite_for(main_program_runner))
suite.addTest(test_cli_main_program__invalid_invokation_dynamic.suite_for(main_program_runner))
suite.addTest(shellcheck_lib_test.default.program_modes.test_suite.suite_for(main_program_runner))

runner = unittest.TextTestRunner()
runner.run(suite)
