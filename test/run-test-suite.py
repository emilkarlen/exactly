"""
A python 3 program that runs the test suite towards the source file structure.
"""
import os
import sys

SRC_DIR_NAME = 'src'

this_dir = sys.path[0]
prj_root_dir = os.path.dirname(this_dir)
src_dir = os.path.join(prj_root_dir, SRC_DIR_NAME)
sys.path.insert(0, src_dir)

os.chdir(this_dir)

from exactly_lib_test.test_resources.main_program.main_program_runners import RunViaOsInSubProcess
import complete_test_suite

main_program_runner = RunViaOsInSubProcess()
complete_test_suite.run_suite_for(main_program_runner)
