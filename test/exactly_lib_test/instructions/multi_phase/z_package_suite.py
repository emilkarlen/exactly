import unittest

from exactly_lib_test.instructions.multi_phase import \
    new_dir, change_dir, \
    run, run_tests_of_instruction_embryo, \
    env, shell
from exactly_lib_test.instructions.multi_phase.define_symbol import z_package_suite as define_symbol
from exactly_lib_test.instructions.multi_phase.new_file import z_package_suite as  new_file
from exactly_lib_test.instructions.multi_phase.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.instructions.multi_phase.utils import z_package_suite as  utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        utils.suite(),
        new_dir.suite(),
        change_dir.suite(),
        new_file.suite(),
        run.suite(),
        run_tests_of_instruction_embryo.suite(),
        env.suite(),
        shell.suite(),
        define_symbol.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
