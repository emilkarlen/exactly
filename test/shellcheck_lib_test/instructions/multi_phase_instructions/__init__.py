import unittest

from shellcheck_lib_test.instructions.multi_phase_instructions import new_dir
from . import change_dir
from . import execute
from . import new_file


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(new_dir.suite())
    ret_val.addTest(change_dir.suite())
    ret_val.addTest(new_file.suite())
    ret_val.addTest(execute.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
