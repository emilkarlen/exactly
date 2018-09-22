import unittest

from exactly_lib_test.instructions.assert_ import z_package_suite as assert_
from exactly_lib_test.instructions.before_assert import z_package_suite as before_assert
from exactly_lib_test.instructions.cleanup import z_package_suite as cleanup
from exactly_lib_test.instructions.configuration import z_package_suite as configuration
from exactly_lib_test.instructions.multi_phase import z_package_suite as multi_phase
from exactly_lib_test.instructions.setup import z_package_suite as setup
from exactly_lib_test.instructions.utils import z_package_suite as utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        utils.suite(),
        configuration.suite(),
        multi_phase.suite(),
        setup.suite(),
        before_assert.suite(),
        assert_.suite(),
        cleanup.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
