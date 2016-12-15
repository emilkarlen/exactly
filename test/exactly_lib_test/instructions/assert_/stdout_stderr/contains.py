import unittest

from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestConfigurationForStdout, \
    TestConfigurationForStderr
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contains as test_resources


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources.suite_for(TestConfigurationForStdout()),
        test_resources.suite_for(TestConfigurationForStderr()),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
