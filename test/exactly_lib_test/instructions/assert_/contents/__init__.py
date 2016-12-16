import unittest

from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib_test.instructions.assert_.contents import empty_with_relativity_option_for_actual_file
from exactly_lib_test.instructions.assert_.contents import equals_with_relativity_option_for_actual_file
from exactly_lib_test.instructions.assert_.contents import parse
from exactly_lib_test.instructions.assert_.contents.test_resources import TestConfigurationForFile
from exactly_lib_test.instructions.assert_.contents.test_resources import TestConfigurationForFile
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contains
from exactly_lib_test.instructions.assert_.test_resources.file_contents import empty
from exactly_lib_test.instructions.assert_.test_resources.file_contents import equals
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    configuration = TestConfigurationForFile()
    return unittest.TestSuite([
        parse.suite(),
        empty.suite_for(configuration),
        empty_with_relativity_option_for_actual_file.suite_for(configuration),
        equals.suite_for(configuration),
        equals_with_relativity_option_for_actual_file.suite_for(configuration),
        contains.suite_for(configuration),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
