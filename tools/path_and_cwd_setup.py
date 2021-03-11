import pathlib
import sys

SRC_DIR_NAME = 'src'
TEST_DIR_NAME = 'test'


def initialize():
    this_dir = pathlib.Path(sys.path[0])
    del sys.path[0]
    src_dir = this_dir.parent / SRC_DIR_NAME
    test_dir = this_dir.parent / TEST_DIR_NAME
    sys.path.insert(0, str(test_dir))
    sys.path.insert(0, str(src_dir))
