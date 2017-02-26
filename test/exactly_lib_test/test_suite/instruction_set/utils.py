import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_suite.instruction_set import utils as sut
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check, equivalent_source_variants


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
    ])


class TestParse(unittest.TestCase):
    def test_fail_when_invalid_syntax(self):
        test_cases = [
            '',
            '   ',
            'token1 token2',
            '\'invalid quoting   ',
        ]
        for instruction_argument in test_cases:
            with self.subTest(msg='instruction argument=' + repr(instruction_argument)):
                for source in equivalent_source_variants(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_file_names_resolver(source)

    def parse_plain_file_name(self):
        # Bad test, since inspects implementation detail of structure, instead of behaviour.
        test_cases = [
            ('file-name.ext', 'file-name.ext'),
            ('\'quoted file name.ext\'', 'quoted file name.ext'),
            ('\'  quoted file name.ext \'', '  quoted file name.ext '),
            ('\'quoted file name with wild-cards **\'', 'quoted file name with wild-cards **'),
        ]
        for instruction_argument, expected_file_name in test_cases:
            with self.subTest(msg='instruction argument=' + repr(instruction_argument)):
                for source in equivalent_source_variants__with_source_check(self, instruction_argument):
                    actual = sut.parse_file_names_resolver(source)
                    self.assertIsInstance(actual, sut.FileNamesResolverForPlainFileName,
                                          'should be ' + str(sut.FileNamesResolverForPlainFileName))
                    assert isinstance(actual, sut.FileNamesResolverForPlainFileName)
                    self.assertEqual(expected_file_name, actual.file_name,
                                     'file name')

    def parse_glob_pattern(self):
        # Bad test, since inspects implementation detail of structure, instead of behaviour.
        test_cases = [
            ('*.abc', '*.abc'),
            ('**a', '**a'),
        ]
        for instruction_argument, expected_pattern in test_cases:
            with self.subTest(msg='instruction argument=' + repr(instruction_argument)):
                for source in equivalent_source_variants__with_source_check(self, instruction_argument):
                    actual = sut.parse_file_names_resolver(source)
                    self.assertIsInstance(actual, sut.FileNamesResolverForGlobPattern,
                                          'should be ' + str(sut.FileNamesResolverForGlobPattern))
                    assert isinstance(actual, sut.FileNamesResolverForGlobPattern)
                    self.assertEqual(expected_pattern, actual.pattern,
                                     'pattern')
