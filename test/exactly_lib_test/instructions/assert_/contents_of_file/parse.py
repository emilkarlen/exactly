import unittest

from exactly_lib.instructions.assert_ import contents_of_file as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.contents_of_file.test_resources.arguments_construction import args
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import equivalent_source_variants


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParse)


class TestParse(unittest.TestCase):
    def test_raise_exception_when_syntax_is_invalid(self):
        test_cases = [
            '',
            args('actual {equals} expected unexpected-extra'),
            args('actual {equals} {not} expected'),
        ]
        parser = sut.Parser()
        for instruction_argument in test_cases:
            with self.subTest(msg=instruction_argument):
                for source in equivalent_source_variants(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)
