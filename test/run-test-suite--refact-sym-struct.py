"""
A python 3 program that runs the test suite towards the source file structure.
"""
import unittest

import path_and_cwd_setup

path_and_cwd_setup.initialize()

import exactly_lib_test.z_package_suite__refact_sym_struct as test_suite_package

runner = unittest.TextTestRunner()
runner.run(test_suite_package.suite_that_does_not_require_main_program_runner())
