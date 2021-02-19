import unittest

from exactly_lib_test.impls.instructions.assert_ import \
    change_dir, \
    run, \
    new_file, \
    new_dir, \
    copy, \
    shell, \
    sys_cmd, \
    env, \
    timeout, \
    define_symbol
from exactly_lib_test.impls.instructions.assert_ import test_resources_test
from exactly_lib_test.impls.instructions.assert_.contents_of_dir import z_package_suite as contents_of_dir
from exactly_lib_test.impls.instructions.assert_.contents_of_file import z_package_suite as contents_of_file
from exactly_lib_test.impls.instructions.assert_.existence_of_file import z_package_suite as existence_of_file
from exactly_lib_test.impls.instructions.assert_.process_output import z_package_suite as process_output
from exactly_lib_test.impls.instructions.assert_.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.impls.instructions.assert_.utils import z_package_suite as utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        utils.suite(),
        define_symbol.suite(),
        contents_of_file.suite(),
        contents_of_dir.suite(),
        process_output.suite(),
        existence_of_file.suite(),
        new_file.suite(),
        new_dir.suite(),
        copy.suite(),
        change_dir.suite(),
        run.suite(),
        sys_cmd.suite(),
        shell.suite(),
        timeout.suite(),
        env.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
