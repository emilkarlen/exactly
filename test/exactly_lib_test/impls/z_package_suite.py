import unittest

from exactly_lib_test.impls import file_properties
from exactly_lib_test.impls.actors import z_package_suite as actors
from exactly_lib_test.impls.exception import z_package_suite as exception
from exactly_lib_test.impls.instructions import z_package_suite as instructions
from exactly_lib_test.impls.program_execution import z_package_suite as program_execution
from exactly_lib_test.impls.types import z_package_suite as types


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        exception.suite(),
        file_properties.suite(),
        program_execution.suite(),
        types.suite(),
        actors.suite(),
        instructions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
