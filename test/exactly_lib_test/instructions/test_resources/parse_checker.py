import unittest
from contextlib import contextmanager

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parsing import LocationAwareParser
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO


class Checker:
    def __init__(self, parser: LocationAwareParser):
        self.parser = parser

    def check_invalid_arguments(self,
                                put: unittest.TestCase,
                                source: ParseSource,
                                ):
        with put.assertRaises(SingleInstructionInvalidArgumentException) as cx:
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

        put.assertIsInstance(cx.exception.error_message,
                             str,
                             'error message')

    def check_valid_arguments(self,
                              put: unittest.TestCase,
                              source: ParseSource,
                              ):
        actual = self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        put.assertIsNotNone(actual,
                            'parsed object')


@contextmanager
def assert_raises_invalid_argument_exception(put: unittest.TestCase):
    with put.assertRaises(SingleInstructionInvalidArgumentException) as cx:
        yield
    put.assertIsInstance(cx.exception.error_message,
                         str,
                         'error message')
