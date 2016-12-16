import unittest

from exactly_lib_test.instructions.assert_.contents.test_resources import TestConfigurationForFile
from exactly_lib_test.instructions.assert_.test_resources.file_contents import empty


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        empty.suite_for(TestConfigurationForFile()),
    ])
