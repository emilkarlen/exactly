import unittest

from exactly_lib_test.instructions.before_assert import \
    define_symbol, change_dir, env, run, shell, new_file, copy, new_dir, sys_cmd
from exactly_lib_test.instructions.before_assert.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.instructions.before_assert.utils import z_package_suite as utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        utils.suite(),
        define_symbol.suite(),
        change_dir.suite(),
        new_file.suite(),
        new_dir.suite(),
        copy.suite(),
        shell.suite(),
        sys_cmd.suite(),
        run.suite(),
        env.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
