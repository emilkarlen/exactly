import unittest

from exactly_lib.section_document import parsed_section_element
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_suite.instruction_set.sections import cases as sut
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check, equivalent_source_variants
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParse)


class TestParse(unittest.TestCase):
    def test_fail_when_invalid_syntax(self):
        test_cases = [
            '',
            '   ',
            'too many tokens',
        ]
        parser = sut.new_parser()
        for instruction_argument in test_cases:
            with self.subTest(msg='instruction argument=' + repr(instruction_argument)):
                for source in equivalent_source_variants(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_succeed_when_valid_syntax(self):
        test_cases = [
            'file-name.ext',
            '**.ext',
            '\'quoted file name ***\'',
        ]
        parser = sut.new_parser()
        for instruction_argument in test_cases:
            with self.subTest(msg='instruction argument=' + repr(instruction_argument)):
                for source in equivalent_source_variants__with_source_check(self, instruction_argument):
                    actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                    self.assertIsInstance(actual,
                                          parsed_section_element.ParsedInstruction)
                    self.assertIsInstance(actual.instruction_info.instruction,
                                          sut.CasesSectionInstruction)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
