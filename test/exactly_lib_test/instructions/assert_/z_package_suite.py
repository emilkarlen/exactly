import unittest

from exactly_lib_test.instructions.assert_ import \
    change_dir, \
    run, \
    exitcode, \
    new_file, \
    new_dir, \
    copy, \
    shell, \
    sys_cmd, \
    env, \
    define_symbol
from exactly_lib_test.instructions.assert_ import stdout, stderr
from exactly_lib_test.instructions.assert_ import test_resources_test
from exactly_lib_test.instructions.assert_.contents_of_dir import z_package_suite as contents_of_dir
from exactly_lib_test.instructions.assert_.contents_of_file import z_package_suite as contents_of_file
from exactly_lib_test.instructions.assert_.existence_of_file import z_package_suite as existence_of_file
from exactly_lib_test.instructions.assert_.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.instructions.assert_.utils import z_package_suite as utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        utils.suite(),
        define_symbol.suite(),
        exitcode.suite(),
        contents_of_file.suite(),
        contents_of_dir.suite(),
        stdout.suite(),
        stderr.suite(),
        existence_of_file.suite(),
        new_file.suite(),
        new_dir.suite(),
        copy.suite(),
        change_dir.suite(),
        run.suite(),
        sys_cmd.suite(),
        shell.suite(),
        env.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
