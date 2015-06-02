import sys
import os
import unittest


SRC_DIR_NAME = 'src'

this_dir = sys.path[0]
prj_root_dir = os.path.dirname(this_dir)
src_dir = os.path.join(prj_root_dir, SRC_DIR_NAME)
sys.path.insert(0, src_dir)

os.chdir(this_dir)

import shellcheck_main_program_test
from shellcheck_lib_test import test_suite as shellcheck_test_suite

suite = unittest.TestSuite()
suite.addTest(shellcheck_test_suite.suite())
suite.addTest(shellcheck_main_program_test.suite())

runner = unittest.TextTestRunner()
runner.run(suite)
