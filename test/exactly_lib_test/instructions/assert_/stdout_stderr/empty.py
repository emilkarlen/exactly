import unittest

from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestConfigurationForStdout, \
    TestConfigurationForStderr
from exactly_lib_test.instructions.assert_.test_resources.file_contents import empty


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        empty.suite_for(TestConfigurationForStdout()),
        empty.suite_for(TestConfigurationForStderr()),
    ])
