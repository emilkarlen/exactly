"""Tests that applies for every contents checking instruction."""

import unittest

from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents import concrete_matcher, symbol_reference
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents import error_from_matcher, \
    string_matcher_should_be_parsed_as_full_expr
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents import parse_invalid_syntax
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration


def suite_for(configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_invalid_syntax.suite_for(configuration),
        symbol_reference.suite_for(configuration),
        error_from_matcher.suite_for(configuration),
        concrete_matcher.suite_for(configuration),
        string_matcher_should_be_parsed_as_full_expr.suite_for(configuration),
    ])
