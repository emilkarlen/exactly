import sys
import os

SRC_DIR_NAME = 'src'

this_dir = sys.path[0]
prj_root_dir = os.path.dirname(this_dir)

src_dir = os.path.join(prj_root_dir, SRC_DIR_NAME)

sys.path.insert(0, src_dir)
os.chdir(os.path.join(this_dir, 'shelltest_test'))

from shelltest_test import test_suite

test_suite.run_suite()
