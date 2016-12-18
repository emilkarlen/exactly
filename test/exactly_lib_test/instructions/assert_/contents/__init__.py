import unittest

from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib_test.instructions.assert_.contents import parse
from exactly_lib_test.instructions.assert_.contents.relativity_option_for_actual_file import \
    contains as contains_with_relative_actual, \
    empty as empty_with_relative_actual, \
    equals as equals_with_relative_actual, \
    equals_with_replaced_env_vars
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
        empty_with_relative_actual.suite_for(configuration),
        equals.suite_for(configuration),
        equals_with_relative_actual.suite_for(configuration),
        equals_with_replaced_env_vars.suite_for(configuration),
        contains.suite_for(configuration),
        contains_with_relative_actual.suite_for(configuration),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
