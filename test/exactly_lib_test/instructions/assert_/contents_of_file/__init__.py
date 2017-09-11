import unittest

from exactly_lib.instructions.assert_ import contents_of_file as sut
from exactly_lib_test.instructions.assert_.contents_of_file import parse
from exactly_lib_test.instructions.assert_.contents_of_file.relativity_option_for_actual_file import \
    any_line_matches as any_line_matches_with_relative_actual, \
    empty as empty_with_relative_actual, \
    equals as equals_with_relative_actual
from exactly_lib_test.instructions.assert_.contents_of_file.test_resources import TestConfigurationForFile
from exactly_lib_test.instructions.assert_.test_resources.file_contents import common_tests
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    configuration = TestConfigurationForFile()
    return unittest.TestSuite([
        common_tests.suite_for(configuration),

        parse.suite(),
        empty_with_relative_actual.suite_for(configuration),
        equals_with_relative_actual.suite_for(configuration),
        any_line_matches_with_relative_actual.suite_for(configuration),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
