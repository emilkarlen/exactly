"""
A python 3 program that runs test cases that depend on the default main program.
"""
import unittest

import path_and_cwd_setup

path_and_cwd_setup.initialize()

from exactly_lib_test.test_resources.main_program.main_program_runners import RunDefaultMainProgramViaOsInSubProcess
import complete_test_suite

mpr = RunDefaultMainProgramViaOsInSubProcess()
suite = complete_test_suite.just_with_main_program_runner_with_default_setup(mpr)
runner = unittest.TextTestRunner()
runner.run(suite)
