import unittest

from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.test_resources.parse import new_source2


class TestParse(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2(''))


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParse)
