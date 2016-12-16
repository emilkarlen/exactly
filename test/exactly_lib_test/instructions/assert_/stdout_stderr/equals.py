import unittest

from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestConfigurationForStdout, \
    TestConfigurationForStderr
from exactly_lib_test.instructions.assert_.test_resources.file_contents import equals


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        equals.suite_for(TestConfigurationForStdout()),
        equals.suite_for(TestConfigurationForStderr()),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
