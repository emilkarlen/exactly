import unittest

import shellcheck_lib_test
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.main_program_runner import \
    RunInstalledProgramViaOsInSubProcess

# This value is from setup.py
EXECUTABLE_NAME = 'shellcheck'

main_program_runner = RunInstalledProgramViaOsInSubProcess(EXECUTABLE_NAME)
suite = unittest.TestSuite()
suite.addTest(shellcheck_lib_test.suite())
suite.addTest(shellcheck_lib_test.default.program_modes.test_case.suite_for(main_program_runner))
suite.addTest(shellcheck_lib_test.default.program_modes.test_suite.suite_for(main_program_runner))

runner = unittest.TextTestRunner()
runner.run(suite)
