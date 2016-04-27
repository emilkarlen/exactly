import unittest

from exactly_lib_test.instructions import act
from exactly_lib_test.instructions import assert_phase
from exactly_lib_test.instructions import before_assert
from exactly_lib_test.instructions import cleanup
from exactly_lib_test.instructions import configuration
from exactly_lib_test.instructions import multi_phase_instructions
from exactly_lib_test.instructions import setup
from exactly_lib_test.instructions import utils


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
