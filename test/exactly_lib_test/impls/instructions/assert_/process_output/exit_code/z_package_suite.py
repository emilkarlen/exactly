import unittest

from exactly_lib_test.impls.instructions.assert_.process_output.exit_code import from_act
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.from_program import \
    z_package_suite as from_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        from_act.suite(),
        from_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
