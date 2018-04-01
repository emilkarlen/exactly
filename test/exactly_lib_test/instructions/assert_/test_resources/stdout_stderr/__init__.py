import unittest

from exactly_lib_test.instructions.assert_.test_resources.file_contents import common_tests
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr import process_output
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.configuration import TestConfigurationForStdFile


def suite_for(configuration: TestConfigurationForStdFile) -> unittest.TestSuite:
    return unittest.TestSuite([
        common_tests.suite_for(configuration),
        process_output.suite_for(configuration),
    ])
