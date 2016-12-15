import unittest

from exactly_lib_test.instructions.assert_.contents.test_resources import TestConfigurationForFile
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contains as test_resources


def suite() -> unittest.TestSuite:
    return test_resources.suite_for(TestConfigurationForFile('actual.txt', 'actual.txt'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
