import unittest

from exactly_lib_test.instructions.multi_phase import \
    new_dir, change_dir, \
    env, shell
from exactly_lib_test.instructions.multi_phase.define_symbol import z_package_suite as define_symbol
from exactly_lib_test.instructions.multi_phase.new_file import z_package_suite as new_file
from exactly_lib_test.instructions.multi_phase.run_program import z_package_suite as run_program
from exactly_lib_test.instructions.multi_phase.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        new_dir.suite(),
        change_dir.suite(),
        new_file.suite(),
        run_program.suite(),
        env.suite(),
        shell.suite(),
        define_symbol.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
