import unittest

import exactly_lib.test_case_utils.files_condition.syntax
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.files_condition import parse as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.string import StringFormatter
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_syntax import \
    NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSyntaxErrorExceptionShouldBeRaisedWhenMissingBeginBrace),
        unittest.makeSuite(TestSyntaxErrorExceptionShouldBeRaisedWhenMissingEndBrace),
        unittest.makeSuite(TestSyntaxErrorExceptionShouldBeRaisedWhenInvalidFileMatcher),
        unittest.makeSuite(TestSyntaxErrorExceptionShouldBeRaisedWhenMultipleFileNamesOnSameLine),
    ])


class _TestCaseHelperBase(unittest.TestCase):
    def _expect_parse_exception(self,
                                source: str,
                                must_be_on_current_line: bool,
                                ):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parser().parse(remaining_source(source),
                               must_be_on_current_line)


class TestSyntaxErrorExceptionShouldBeRaisedWhenMissingBeginBrace(_TestCaseHelperBase):
    def test_missing_start_brace(self):
        cases = [
            NameAndValue(
                'empty source',
                ''
            ),
            NameAndValue(
                'quoted start brace token',
                surrounded_by_hard_quotes_str(exactly_lib.test_case_utils.files_condition.syntax.BEGIN_BRACE)
            ),
            NameAndValue(
                'non start brace token',
                exactly_lib.test_case_utils.files_condition.syntax.END_BRACE
            ),
        ]
        for must_be_on_current_line in [False, True]:
            for case in cases:
                with self.subTest(source_case=case.name,
                                  must_be_on_current_line=must_be_on_current_line):
                    self._expect_parse_exception(case.value, must_be_on_current_line)

    def test_begin_brace_on_following_line_BUT_must_be_on_current_line(self):
        self._expect_parse_exception('\n{}'.format(exactly_lib.test_case_utils.files_condition.syntax.BEGIN_BRACE),
                                     must_be_on_current_line=True)


class TestSyntaxErrorExceptionShouldBeRaisedWhenMissingEndBrace(_TestCaseHelperBase):
    def test_begin_brace_on_current_line(self):
        cases = [
            NameAndValue(
                'empty set',
                '{BEGIN_BRACE}'
            ),
            NameAndValue(
                'set with single file name',
                '{BEGIN_BRACE} file-name'
            ),
            NameAndValue(
                'set with multiple file names',
                '{BEGIN_BRACE} file-name1\nfile-name2  '
            ),
            NameAndValue(
                'set with single file name and file matcher',
                '{BEGIN_BRACE} file-name {FILE_MATCHER_SEPARATOR} {FILE_MATCHER}'
            ),
        ]
        for must_be_on_current_line in [False, True]:
            for case in cases:
                with self.subTest(source_case=case.name,
                                  must_be_on_current_line=must_be_on_current_line):
                    source = _SF.format(case.value)
                    self._expect_parse_exception(case.value, must_be_on_current_line)

    def test_begin_brace_on_following(self):
        cases = [
            NameAndValue(
                'empty set',
                '\n{BEGIN_BRACE}'
            ),
            NameAndValue(
                'set with single file name',
                '\n {BEGIN_BRACE} file-name'
            ),
            NameAndValue(
                'set with multiple file names',
                '\n{BEGIN_BRACE} file-name1\nfile-name2  '
            ),
            NameAndValue(
                'set with single file name and file matcher',
                '\n{BEGIN_BRACE} file-name {FILE_MATCHER_SEPARATOR} {FILE_MATCHER}'
            ),
        ]
        for case in cases:
            with self.subTest(source_case=case.name):
                source = _SF.format(case.value)
                self._expect_parse_exception(source, must_be_on_current_line=False)


class TestSyntaxErrorExceptionShouldBeRaisedWhenInvalidFileMatcher(_TestCaseHelperBase):
    def test(self):
        cases = [
            NameAndValue(
                'missing matcher after matcher separator (and missing end brace)',
                '{BEGIN_BRACE} file-name {FILE_MATCHER_SEPARATOR}'
            ),
            NameAndValue(
                'missing matcher after matcher separator',
                '{BEGIN_BRACE} file-name {FILE_MATCHER_SEPARATOR} {END_BRACE}'
            ),
            NameAndValue(
                'invalid matcher after matcher separator',
                '{BEGIN_BRACE} file-name {FILE_MATCHER_SEPARATOR} {INVALID_FILE_MATCHER} {END_BRACE}'
            ),
        ]
        for must_be_on_current_line in [False, True]:
            for case in cases:
                with self.subTest(source_case=case.name,
                                  must_be_on_current_line=must_be_on_current_line):
                    source = _SF.format(case.value)
                    self._expect_parse_exception(source, must_be_on_current_line)


class TestSyntaxErrorExceptionShouldBeRaisedWhenMultipleFileNamesOnSameLine(_TestCaseHelperBase):
    def test(self):
        cases = [
            NameAndValue(
                'multiple file names on one and only line',
                '{BEGIN_BRACE} fn1 fn2  {END_BRACE}'
            ),
            NameAndValue(
                'first line ok, multiple file names on second line',
                '{BEGIN_BRACE} file-name\n'
                'fn1 fn2\n'
                '{END_BRACE}'
            ),
        ]
        for must_be_on_current_line in [False, True]:
            for case in cases:
                with self.subTest(source_case=case.name,
                                  must_be_on_current_line=must_be_on_current_line):
                    source = _SF.format(case.value)
                    self._expect_parse_exception(source, must_be_on_current_line)


_SF = StringFormatter({
    'BEGIN_BRACE': exactly_lib.test_case_utils.files_condition.syntax.BEGIN_BRACE,
    'END_BRACE': exactly_lib.test_case_utils.files_condition.syntax.END_BRACE,
    'FILE_MATCHER_SEPARATOR': exactly_lib.test_case_utils.files_condition.syntax.FILE_MATCHER_SEPARATOR,
    'FILE_NAME': 'a-file-name',
    'FILE_MATCHER': 'file_matcher_symbol',
    'INVALID_FILE_MATCHER': NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME,
})
