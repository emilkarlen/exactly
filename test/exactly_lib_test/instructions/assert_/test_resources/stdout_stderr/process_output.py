import unittest

from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.configuration import TestConfigurationForStdFile


def suite_for(conf: TestConfigurationForStdFile) -> unittest.TestSuite:
    return unittest.TestSuite([])

