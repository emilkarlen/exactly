import unittest

from exactly_lib_test.impls.instructions.multi_phase import \
    change_dir, \
    shell, sys_cmd
from exactly_lib_test.impls.instructions.multi_phase.new_dir import z_package_suite as new_dir
from exactly_lib_test.impls.instructions.multi_phase.copy_ import z_package_suite as copy_
from exactly_lib_test.impls.instructions.multi_phase.define_symbol import z_package_suite as define_symbol
from exactly_lib_test.impls.instructions.multi_phase.environ import z_package_suite as env
from exactly_lib_test.impls.instructions.multi_phase.new_file import z_package_suite as new_file
from exactly_lib_test.impls.instructions.multi_phase.run_program import z_package_suite as run_program
from exactly_lib_test.impls.instructions.multi_phase.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.impls.instructions.multi_phase.timeout import z_package_suite as timeout


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        timeout.suite(),
        new_dir.suite(),
        change_dir.suite(),
        new_file.suite(),
        copy_.suite(),
        run_program.suite(),
        env.suite(),
        sys_cmd.suite(),
        shell.suite(),
        define_symbol.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
