import unittest

from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.num_lines import \
    invalid_syntax_test_cases, operand_expression_test_cases, valid_syntax_test_cases


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax_test_cases.suite_for(configuration),
        operand_expression_test_cases.suite_for(configuration),
        valid_syntax_test_cases.suite_for(configuration),
    ])