import os
import sys
import unittest

SRC_DIR_NAME = 'src'

this_dir = sys.path[0]
prj_root_dir = os.path.dirname(this_dir)
src_dir = os.path.join(prj_root_dir, SRC_DIR_NAME)
sys.path.insert(0, src_dir)

os.chdir(this_dir)

import shellcheck_lib_test
from shellcheck_lib_test.test_resources.main_program.main_program_runners import RunViaOsInSubProcess

main_program_runner = RunViaOsInSubProcess()
suite = unittest.TestSuite()
suite.addTest(shellcheck_lib_test.suite())
suite.addTest(shellcheck_lib_test.default.program_modes.test_case.suite_for(main_program_runner))
suite.addTest(shellcheck_lib_test.default.program_modes.test_suite.suite_for(main_program_runner))

runner = unittest.TextTestRunner()
runner.run(suite)
