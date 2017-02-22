import unittest

from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.test_resources.parse import remaining_source


class TestParse(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.parse,
                          remaining_source(''))


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParse)
