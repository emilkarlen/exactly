"""
Runs all tests that does not require a MainProgramRunner - i.e. skips many of the slow tests.
"""
import os
import sys

SRC_DIR_NAME = 'src'

this_dir = sys.path[0]
prj_root_dir = os.path.dirname(this_dir)
src_dir = os.path.join(prj_root_dir, SRC_DIR_NAME)
sys.path.insert(0, src_dir)

os.chdir(this_dir)

import unittest
import exactly_lib_test

suite = exactly_lib_test.suite_that_does_not_require_main_program_runner()
runner = unittest.TextTestRunner()
runner.run(suite)
