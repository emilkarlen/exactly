import unittest

from exactly_lib_test.util.process_execution import sub_process_execution, commands, executable_factories


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        sub_process_execution.suite(),
        commands.suite(),
        executable_factories.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
