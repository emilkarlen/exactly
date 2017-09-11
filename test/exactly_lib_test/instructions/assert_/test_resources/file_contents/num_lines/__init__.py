import unittest

from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.num_lines import \
    invalid_syntax_test_cases


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax_test_cases.suite_for(configuration),
    ])
