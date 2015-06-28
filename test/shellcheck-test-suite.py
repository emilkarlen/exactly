import sys
import os
import unittest


SRC_DIR_NAME = 'src'

this_dir = sys.path[0]
prj_root_dir = os.path.dirname(this_dir)
src_dir = os.path.join(prj_root_dir, SRC_DIR_NAME)
sys.path.insert(0, src_dir)

os.chdir(this_dir)

import shellcheck_cli_main_program_test
import shellcheck_lib_test

suite = unittest.TestSuite()
suite.addTest(shellcheck_lib_test.suite())
suite.addTest(shellcheck_cli_main_program_test.suite())

runner = unittest.TextTestRunner()
runner.run(suite)
