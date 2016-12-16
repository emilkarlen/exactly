import unittest

from exactly_lib_test.instructions.assert_.contents.test_resources import TestConfigurationForFile
from exactly_lib_test.instructions.assert_.test_resources.file_contents import equals
from . import equals_with_relativity_option_for_actual_file


def suite() -> unittest.TestSuite:
    test_configuration_for_file = TestConfigurationForFile()
    return unittest.TestSuite([
        equals.suite_for(test_configuration_for_file),
        equals_with_relativity_option_for_actual_file.suite_for(test_configuration_for_file),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
