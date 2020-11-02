import unittest

from exactly_lib.impls.instructions.assert_ import contents_of_file as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.impls.types.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParse)


class TestParse(unittest.TestCase):
    def test_raise_exception_when_syntax_is_invalid(self):
        test_cases = [
            '',
            args('actual {equals} expected unexpected-extra'),
            args('actual {equals} {not} expected'),
        ]
        parser = sut.parser('the-instruction-name')
        for instruction_argument in test_cases:
            with self.subTest(msg=instruction_argument):
                for source in equivalent_source_variants(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
