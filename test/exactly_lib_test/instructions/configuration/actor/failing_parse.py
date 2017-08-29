import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.section_document.test_resources.parse_source import source4


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseForAnyActor),
        unittest.makeSuite(TestFailingParseForCommandLineActor),
        unittest.makeSuite(TestFailingParseForSourceInterpreterActor),
    ])


class TestFailingParseForAnyActor(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = source4('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().parse(source)

    def test_fail_when_the_quoting_is_invalid(self):
        source = source4('argument-1 "argument-2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().parse(source)


class TestFailingParseForCommandLineActor(unittest.TestCase):
    def test_fail_when_extra_unexpected_argument(self):
        source = source4(actor_utils.COMMAND_LINE_ACTOR_OPTION + ' extra-unexpected-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().parse(source)


class TestFailingParseForSourceInterpreterActor(unittest.TestCase):
    def test_fail_when_missing_program_argument(self):
        source = source4(actor_utils.SOURCE_INTERPRETER_OPTION)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().parse(source)
