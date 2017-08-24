import unittest

from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.test_case_utils import token_stream_parse_prime as sut
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseOptionalCommand),
    ])


class TestParseOptionalCommand(unittest.TestCase):
    def test_return_none_WHEN_command_not_found(self):
        command_name = 'command'
        command_parser = do_return('parser return value')
        command_name_2_parser = {
            command_name: command_parser,
        }
        cases = [
            NameAndValue('source is at eof',
                         ''),
            NameAndValue('command name does not match',
                         'nonCommand'),
            NameAndValue('command name is quoted',
                         SOFT_QUOTE_CHAR + command_name + SOFT_QUOTE_CHAR),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                # ARRANGE #
                token_stream = TokenStream(case.value)
                parser = sut.TokenParserPrime(token_stream)
                # ACT #
                actual = parser.parse_optional_command(command_name_2_parser)
                # ASSERT #
                self.assertIsNone(actual)

    def test_return_value_from_parser_WHEN_command_is_found(self):
        command_name = 'command'
        return_value_from_parser = 'parser return value'
        command_parser = do_return(return_value_from_parser)
        command_name_2_parser = {
            command_name: command_parser,
        }
        # ARRANGE #
        token_stream = TokenStream(command_name)
        parser = sut.TokenParserPrime(token_stream)
        # ACT #
        actual = parser.parse_optional_command(command_name_2_parser)
        # ASSERT #
        self.assertEqual(return_value_from_parser,
                         actual)
