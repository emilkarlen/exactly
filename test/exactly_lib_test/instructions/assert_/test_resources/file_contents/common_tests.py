"""Tests that applies for every contents checking instruction."""

import unittest

from exactly_lib_test.instructions.assert_.test_resources.file_contents import empty, equals, symbol_reference
from exactly_lib_test.instructions.assert_.test_resources.file_contents import line_matches, num_lines
from exactly_lib_test.instructions.assert_.test_resources.file_contents import parse_invalid_syntax, \
    parse_with_line_breaks
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals


def suite_for(configuration: InstructionTestConfigurationForEquals) -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_invalid_syntax.suite_for(configuration),
        parse_with_line_breaks.suite_for(configuration),
        empty.suite_for(configuration),
        equals.suite_for(configuration),
        line_matches.suite_for(configuration),
        num_lines.suite_for(configuration),
        symbol_reference.suite_for(configuration),
    ])
