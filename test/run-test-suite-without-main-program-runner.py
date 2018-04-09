"""
Runs all tests that does not require a MainProgramRunner - i.e. skips many of the slow tests.
"""

import path_and_cwd_setup

path_and_cwd_setup.initialize()

import unittest
import complete_test_suite

suite = complete_test_suite.complete_without_main_program_runner()
runner = unittest.TextTestRunner()
runner.run(suite)
