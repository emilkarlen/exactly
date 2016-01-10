import unittest

from shellcheck_lib_test.instructions import act
from shellcheck_lib_test.instructions import assert_phase
from shellcheck_lib_test.instructions import before_assert
from shellcheck_lib_test.instructions import cleanup
from shellcheck_lib_test.instructions import configuration
from shellcheck_lib_test.instructions import multi_phase_instructions
from shellcheck_lib_test.instructions import setup
from shellcheck_lib_test.instructions import utils


def suite():
    return unittest.TestSuite([
        utils.suite(),
        act.suite(),
        multi_phase_instructions.suite(),
        configuration.suite(),
        setup.suite(),
        before_assert.suite(),
        assert_phase.suite(),
        cleanup.suite(),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
