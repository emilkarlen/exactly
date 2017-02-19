import unittest

from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_here_document(self):
        source = remaining_source('<<MARKER',
                                  ['contents',
                                   'MARKER',
                                   'Line 4'])
        actual = sut.parse_from_parse_source(source)
        self.assertTrue(actual.is_here_document,
                        'is_here_document')
        assert_source(current_line_number=asrt.equals(4),
                      remaining_part_of_current_line=asrt.equals('Line 4'))

    def test_invalid_here_document(self):
        source = remaining_source('<<marker',
                                  ['contents',
                                   'nonMarker'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_from_parse_source(source)

    def test_file_ref(self):
        source = remaining_source('file following args',
                                  ['following line'])
        actual = sut.parse_from_parse_source(source)
        self.assertFalse(actual.is_here_document,
                         'is_here_document')
        assert_source(current_line_number=asrt.equals(1),
                      remaining_part_of_current_line=asrt.equals(' following args'))
