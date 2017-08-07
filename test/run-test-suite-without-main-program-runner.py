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
import complete_test_suite

suite = complete_test_suite.complete_without_main_program_runner()
runner = unittest.TextTestRunner()
runner.run(suite)
