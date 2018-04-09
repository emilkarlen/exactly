"""
A python 3 program that runs the test suite towards the source file structure.
"""
import os
import pathlib
import sys
import unittest

SRC_DIR_NAME = 'src'

this_dir = pathlib.Path(sys.path[0])
src_dir = this_dir.parent / SRC_DIR_NAME
sys.path.insert(0, str(src_dir))

os.chdir(str(this_dir))

from exactly_lib_test.test_resources.main_program.main_program_runners import RunDefaultMainProgramViaOsInSubProcess
import complete_test_suite

mpr = RunDefaultMainProgramViaOsInSubProcess()
suite = complete_test_suite.complete_with_main_program_runner_with_default_setup(mpr)
runner = unittest.TextTestRunner()
runner.run(suite)
