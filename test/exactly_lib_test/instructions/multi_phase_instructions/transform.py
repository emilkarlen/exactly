import unittest

from exactly_lib.instructions.multi_phase_instructions import transform as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestWithoutTransformation),
    ])


class TestFailingParse(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        parser = sut.EmbryoParser()
        source = remaining_source('')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(source)


class TestWithoutTransformation(unittest.TestCase):
    def test(self):
        source = remaining_source('f g')
        parser = sut.EmbryoParser()
        parser.parse(source)
