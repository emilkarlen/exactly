import unittest

from exactly_lib.instructions.multi_phase_instructions import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_resources import *


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFailingParseDueToInvalidSyntax)


FAILING_SYNTAX_CASES = [
    ('', 'Empty source'),
    ('not_a_type val_name = value', 'Invalid type name'),
    ('"not_a_type val_name = value', 'Invalid quoting at beginning of type name'),
    ('{string_type} val_name = va"lue', 'Invalid quoting in value'),
    ('{valid_type} "val_name" = {valid_value}', 'VAL-NAME must not be quoted'),
    ('{valid_type} val-name = {valid_value}', 'VAL-NAME must only contain alphanum and _'),
    ('{valid_type} val_name1 val_name2 = {valid_value}', 'Duplicate VAL-NAME'),
    ('{valid_type} name {valid_value}', 'Missing ='),
]


class TestFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        parser = sut.EmbryoParser()
        for (source_str, case_name) in FAILING_SYNTAX_CASES:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)
