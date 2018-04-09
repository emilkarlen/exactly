import os
import pathlib
import sys

SRC_DIR_NAME = 'src'


def initialize():
    this_dir = pathlib.Path(sys.path[0])
    src_dir = this_dir.parent / SRC_DIR_NAME
    sys.path.insert(0, str(src_dir))

    os.chdir(str(this_dir))
