__author__ = 'emil'

import sys
import os.path

this_dir = sys.path[0]
prj_root_dir = os.path.dirname(this_dir)

src_dir = os.path.join(prj_root_dir, 'src')
test_dir = os.path.join(prj_root_dir, 'test')

sys.path.insert(0, src_dir)
sys.path.insert(0, test_dir)

from shelltest_test import test_suite

if __name__ == '__main__':
    test_suite.run_suite()
