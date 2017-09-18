import unittest

from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.line_matches import \
    common_test_cases, valid_syntax_test_cases__any, valid_syntax_test_cases__every


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    return unittest.TestSuite([
        common_test_cases.suite_for(configuration),
        valid_syntax_test_cases__any.suite_for(configuration),
        valid_syntax_test_cases__every.suite_for(configuration),
    ])
