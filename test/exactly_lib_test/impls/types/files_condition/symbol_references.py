import unittest

from exactly_lib.impls.types.files_condition import parse as sut
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.files_condition.test_resources import arguments_building as args
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string_.test_resources.reference_assertions import \
    is_sym_ref_to_string__w_all_indirect_refs_are_strings
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.references import is_reference_to_file_matcher


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSymbolReferenceReporting(),
    ])


class TestSymbolReferenceReporting(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NIE(
                'file name reference',
                [is_sym_ref_to_string__w_all_indirect_refs_are_strings(STRING_SYMBOL_NAME)],
                args.FilesCondition([
                    args.FileCondition(SymbolWithReferenceSyntax(STRING_SYMBOL_NAME)),
                ]),
            ),
            NIE(
                'file name reference (embedded)',
                [is_sym_ref_to_string__w_all_indirect_refs_are_strings(STRING_SYMBOL_NAME)],
                args.FilesCondition([
                    args.FileCondition(
                        'file-name-prefix-' +
                        str(SymbolWithReferenceSyntax(STRING_SYMBOL_NAME)) +
                        '-suffix'
                    ),
                ]),
            ),
            NIE(
                'file matcher reference',
                [is_reference_to_file_matcher(FILE_MATCHER_SYMBOL_NAME)],
                args.FilesCondition([
                    args.FileCondition(
                        'constant-file-name',
                        fm_args.SymbolReferenceWReferenceSyntax(FILE_MATCHER_SYMBOL_NAME)
                    ),
                ]),
            ),
            NIE(
                'file name and file matcher reference',
                [
                    is_sym_ref_to_string__w_all_indirect_refs_are_strings(STRING_SYMBOL_NAME),
                    is_reference_to_file_matcher(FILE_MATCHER_SYMBOL_NAME),
                ],
                args.FilesCondition([
                    args.FileCondition(
                        SymbolWithReferenceSyntax(STRING_SYMBOL_NAME),
                        fm_args.SymbolReferenceWReferenceSyntax(FILE_MATCHER_SYMBOL_NAME)
                    ),
                ]),
            ),
            NIE(
                'multiple file name and file matcher reference',
                [
                    is_sym_ref_to_string__w_all_indirect_refs_are_strings(STRING_SYMBOL_NAME),
                    is_reference_to_file_matcher(FILE_MATCHER_SYMBOL_NAME),
                    is_sym_ref_to_string__w_all_indirect_refs_are_strings(STRING_SYMBOL_NAME_2),
                    is_reference_to_file_matcher(FILE_MATCHER_SYMBOL_NAME_2),
                ],
                args.FilesCondition([
                    args.FileCondition(
                        SymbolWithReferenceSyntax(STRING_SYMBOL_NAME),
                        fm_args.SymbolReferenceWReferenceSyntax(FILE_MATCHER_SYMBOL_NAME),
                    ),
                    args.FileCondition(
                        SymbolWithReferenceSyntax(STRING_SYMBOL_NAME_2),
                        fm_args.SymbolReferenceWReferenceSyntax(FILE_MATCHER_SYMBOL_NAME_2),
                    ),
                ]),
            ),
        ]
        for must_be_on_current_line in [False, True]:
            for case in cases:
                with self.subTest(case=case.name,
                                  must_be_on_current_line=must_be_on_current_line):
                    # ACT #
                    actual = sut.parsers(must_be_on_current_line).full.parse(case.input_value.as_remaining_source)
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
