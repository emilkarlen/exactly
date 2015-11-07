import unittest

from shellcheck_lib_test.instructions import utils
from . import assert_phase
from . import setup
from . import cleanup
from . import configuration


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(utils.suite())
    ret_val.addTest(configuration.suite())
    ret_val.addTest(setup.suite())
    ret_val.addTest(assert_phase.suite())
    ret_val.addTest(cleanup.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
