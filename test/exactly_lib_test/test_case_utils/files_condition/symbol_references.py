import unittest

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.files_condition import parse as sut
from exactly_lib.util.string import StringFormatter
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to__ref
from exactly_lib_test.symbol.test_resources.string import is_string_made_up_of_just_strings_reference_to
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSymbolReferenceReporting(),
    ])


class TestSymbolReferenceReporting(unittest.TestCase):
    def runTest(self):
        cases = [
            NIE(
                'file name reference',
                [is_string_made_up_of_just_strings_reference_to(STRING_SYMBOL_NAME)],
                '{BEGIN_BRACE} {STRING_SYMBOL_NAME_SYM_REF} {END_BRACE}',
            ),
            NIE(
                'file name reference (embedded)',
                [is_string_made_up_of_just_strings_reference_to(STRING_SYMBOL_NAME)],
                '{BEGIN_BRACE} file-name-prefix-{STRING_SYMBOL_NAME_SYM_REF}-suffix {END_BRACE}',
            ),
            NIE(
                'file matcher reference',
                [is_file_matcher_reference_to__ref(FILE_MATCHER_SYMBOL_NAME)],
                '{BEGIN_BRACE} constant-file-name {FILE_MATCHER_SEPARATOR} '
                '{FILE_MATCHER_SYMBOL_NAME_SYM_REF} {END_BRACE}',
            ),
            NIE(
                'file name and file matcher reference',
                [
                    is_string_made_up_of_just_strings_reference_to(STRING_SYMBOL_NAME),
                    is_file_matcher_reference_to__ref(FILE_MATCHER_SYMBOL_NAME),
                ],
                '{BEGIN_BRACE} {STRING_SYMBOL_NAME_SYM_REF} {FILE_MATCHER_SEPARATOR} '
                '{FILE_MATCHER_SYMBOL_NAME_SYM_REF} {END_BRACE}',
            ),
            NIE(
                'multiple file name and file matcher reference',
                [
                    is_string_made_up_of_just_strings_reference_to(STRING_SYMBOL_NAME),
                    is_file_matcher_reference_to__ref(FILE_MATCHER_SYMBOL_NAME),
                    is_string_made_up_of_just_strings_reference_to(STRING_SYMBOL_NAME_2),
                    is_file_matcher_reference_to__ref(FILE_MATCHER_SYMBOL_NAME_2),
                ],
                '{BEGIN_BRACE} \n'
                '{STRING_SYMBOL_NAME_SYM_REF}   {FILE_MATCHER_SEPARATOR} '
                '{FILE_MATCHER_SYMBOL_NAME_SYM_REF}   \n'
                '{STRING_SYMBOL_NAME_SYM_REF_2} {FILE_MATCHER_SEPARATOR} '
                '{FILE_MATCHER_SYMBOL_NAME_SYM_REF_2} \n'
                '{END_BRACE}',
            ),
        ]
        for must_be_on_current_line in [False, True]:
            for case in cases:
                # ACT #
                source = _SF.format(case.input_value)
                actual = sut.parser().parse(remaining_source(case.input_value),
                                            must_be_on_current_line=must_be_on_current_line)
                # ASSERT #
                expectation = asrt.matches_sequence(case.expected_value)
                expectation.apply_without_message(
                    self,
                    actual.references,
                )


STRING_SYMBOL_NAME = 'a_valid_symbol_name__string'
FILE_MATCHER_SYMBOL_NAME = 'a_valid_symbol_name__file_matcher'

STRING_SYMBOL_NAME_2 = 'a_valid_symbol_name__string_2'
FILE_MATCHER_SYMBOL_NAME_2 = 'a_valid_symbol_name__file_matcher_2'

_SF = StringFormatter({
    'BEGIN_BRACE': sut.BEGIN_BRACE,
    'END_BRACE': sut.END_BRACE,
    'FILE_MATCHER_SEPARATOR': sut.FILE_MATCHER_SEPARATOR,
    'STRING_SYMBOL_NAME_SYM_REF': symbol_reference_syntax_for_name(STRING_SYMBOL_NAME),
    'FILE_MATCHER_SYMBOL_NAME_SYM_REF': symbol_reference_syntax_for_name(FILE_MATCHER_SYMBOL_NAME),
    'STRING_SYMBOL_NAME_SYM_REF_2': symbol_reference_syntax_for_name(STRING_SYMBOL_NAME_2),
    'FILE_MATCHER_SYMBOL_NAME_SYM_REF_2': symbol_reference_syntax_for_name(FILE_MATCHER_SYMBOL_NAME_2),
})
