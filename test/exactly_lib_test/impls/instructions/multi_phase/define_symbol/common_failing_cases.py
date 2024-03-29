import unittest

from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.impls.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import \
    remaining_source
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources.symbol_syntax import A_VALID_SYMBOL_NAME


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseDueToInvalidSyntax),
        unittest.makeSuite(TestFailingParseWithInvalidSyntaxAfterValidType),
    ])


INVALID_SYNTAX_CASES = [
    ('', 'Empty source'),
    ('not_a_type val_name = value', 'Invalid type name'),
    ('"not_a_type val_name = value', 'Invalid quoting at beginning of type name'),
]

INVALID_SYNTAX_WITH_VALID_TYPE_CASES = [
    ('{valid_type} "val_name" = {valid_value}', 'VAL-NAME must not be quoted'),
    ('{valid_type} val-name = {valid_value}', 'VAL-NAME must only contain alphanum and _'),
    ('{valid_type} val_name1 val_name2 = {valid_value}', 'Duplicate VAL-NAME'),
    ('{valid_type} name {valid_value}', 'Missing ='),
]


class TestFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        parser = sut.EmbryoParser()
        for (source_str, case_name) in INVALID_SYNTAX_CASES:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestFailingParseWithInvalidSyntaxAfterValidType(unittest.TestCase):
    def runTest(self):
        parser = sut.EmbryoParser()
        for (source_str, case_name) in INVALID_SYNTAX_WITH_VALID_TYPE_CASES:
            for value_type in ValueType:
                type_ident = ANY_TYPE_INFO_DICT[value_type].identifier
                source_str = source_str.format(valid_type=type_ident,
                                               valid_value=A_VALID_SYMBOL_NAME)
                source = remaining_source(source_str)
                with self.subTest(type=type_ident,
                                  msg=case_name):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
