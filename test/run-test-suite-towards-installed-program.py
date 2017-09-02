"""
A python 3 program that runs the test suite towards an installed program.
"""
import unittest

import complete_test_suite
from exactly_lib import program_info
from exactly_lib_test.default.test_resources.installed_program_main_program_runner import \
    RunInstalledProgramViaOsInSubProcess

# This value is from setup.py
EXECUTABLE_NAME = program_info.PROGRAM_NAME

mpr = RunInstalledProgramViaOsInSubProcess(EXECUTABLE_NAME)
suite = complete_test_suite.complete_with_main_program_runner_with_default_setup(mpr)
runner = unittest.TextTestRunner()
runner.run(suite)
