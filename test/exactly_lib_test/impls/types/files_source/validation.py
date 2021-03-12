import unittest
from typing import Sequence, Mapping, List

from exactly_lib.impls.types.files_source import defs
from exactly_lib.impls.types.files_source.defs import FileType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as abs_stx
from exactly_lib_test.impls.types.files_source.test_resources import integration_check, models
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import LiteralFilesSourceAbsStx, \
    FileSpecAbsStx, ContentsAbsStx
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.impls.types.string_source.test_resources import \
    validation_cases as str_src_validation_cases
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.type_val_deps.test_resources.validation_case import ValidationCaseWSymbolContextAndAssertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_rest
from exactly_lib_test.type_val_deps.types.files_source.test_resources import \
    validation_cases as file_src_validation_cases
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualFileNames),
        unittest.makeSuite(TestFileMaker),
    ])


class ContentsCase:
    def __init__(self,
                 modification_type: defs.ModificationType,
                 other_valid_file_spec: NameAndValue[List[FileSpecAbsStx]],
                 ):
        self.modification_type = modification_type
        self.other_valid_file_spec = other_valid_file_spec

    @staticmethod
    def cases() -> Sequence['ContentsCase']:
        return [
            ContentsCase(modification_type, other_valid_file_spec)
            for modification_type in defs.ModificationType
            for other_valid_file_spec in OTHER_VALID_FILE_SPECS
        ]


class TestFileMaker(unittest.TestCase):
    def test_directory(self):
        # ARRANGE #
        valid_file_name = StringLiteralAbsStx('valid_file_name')
        for validation_case in file_src_validation_cases.failing_validation_cases():
            symbol_context = validation_case.value.symbol_context
            for contents_case in ContentsCase.cases():
                invalid_file_spec = abs_stx.dir_spec(
                    valid_file_name,
                    abs_stx.DirContentsExplicitAbsStx(contents_case.modification_type,
                                                      symbol_context.abstract_syntax),
                )
                # ACT & ASSERT #
                self._check_case(
                    invalid_file_spec,
                    contents_case,
                    validation_case,
                )

    def test_regular_file(self):
        valid_file_name = StringLiteralAbsStx('valid_file_name')
        for validation_case in str_src_validation_cases.failing_validation_cases():
            symbol_context = validation_case.value.symbol_context
            for contents_case in ContentsCase.cases():
                invalid_file_spec = abs_stx.regular_file_spec(
                    valid_file_name,
                    abs_stx.FileContentsExplicitAbsStx(contents_case.modification_type,
                                                       symbol_context.abstract_syntax),
                )
                # ACT & ASSERT #
                self._check_case(
                    invalid_file_spec,
                    contents_case,
                    validation_case,
                )

    def _check_case(self,
                    invalid_file_spec: FileSpecAbsStx,
                    contents_case: ContentsCase,
                    validation_case: NameAndValue[ValidationCaseWSymbolContextAndAssertion],
                    ):
        symbol_context = validation_case.value.symbol_context
        integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
            self,
            LiteralFilesSourceAbsStx(contents_case.other_valid_file_spec.value + [invalid_file_spec]),
            models.empty(),
            arrangement_wo_tcds(
                symbols=symbol_context.symbol_table
            ),
            MultiSourceExpectation(
                symbol_references=symbol_context.references_assertion,
                execution=ExecutionExpectation(
                    validation=validation_case.value.assertion
                )
            ),
            sub_test_identifiers={
                'validation': validation_case.name,
                'other-valid-file-spec': contents_case.other_valid_file_spec.name,
                'modification-type': contents_case.modification_type,
            }
        )


class TestIndividualFileNames(unittest.TestCase):
    def test_string_literal(self):
        for other_valid_file_spec_case in OTHER_VALID_FILE_SPECS:
            for file_name_case in INVALID_FILE_NAMES:
                file_name_abs_stx = StringLiteralAbsStx(file_name_case.value, QuoteType.HARD)
                for file_spec_case in file_type_and_contents_variants(file_name_abs_stx):
                    integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
                        self,
                        LiteralFilesSourceAbsStx(other_valid_file_spec_case.value + [file_spec_case.value]),
                        models.empty(),
                        arrangement_wo_tcds(),
                        MultiSourceExpectation(
                            execution=ExecutionExpectation(
                                validation=ValidationAssertions.pre_sds_fails__w_any_msg()
                            )
                        ),
                        sub_test_identifiers={
                            'file-name': file_name_case.name,
                            'type-and-contents': file_spec_case.name,
                            'other-valid-file-spec': other_valid_file_spec_case.name,
                        }
                    )

    def test_string_symbol_reference(self):
        for other_valid_file_spec_case in OTHER_VALID_FILE_SPECS:
            for file_name_case in INVALID_FILE_NAMES:
                file_name_symbol = StringSymbolContext.of_constant(
                    'FILE_NAME_SYMBOL',
                    file_name_case.value,
                    default_restrictions=asrt_rest.is__string__w_all_indirect_refs_are_strings(),
                )
                file_name_abs_stx = file_name_symbol.abstract_syntax
                for file_spec_case in file_type_and_contents_variants(file_name_abs_stx):
                    integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
                        self,
                        LiteralFilesSourceAbsStx(other_valid_file_spec_case.value + [file_spec_case.value]),
                        models.empty(),
                        arrangement_wo_tcds(
                            symbols=file_name_symbol.symbol_table
                        ),
                        MultiSourceExpectation(
                            symbol_references=file_name_symbol.references_assertion,
                            execution=ExecutionExpectation(
                                validation=ValidationAssertions.pre_sds_fails__w_any_msg()
                            )
                        ),
                        sub_test_identifiers={
                            'file-name': file_name_case.name,
                            'type-and-contents': file_spec_case.name,
                            'other-valid-file-spec': other_valid_file_spec_case.name,
                        }
                    )


INVALID_FILE_NAMES: Sequence[NameAndValue[str]] = [
    NameAndValue('empty', ''),
    NameAndValue('absolute', '/a/b/c'),
    NameAndValue('relative component (double dot)', 'b/../c'),
    NameAndValue('os path separator (posix)', 'a/:b/c'),
    NameAndValue('os path separator (windows)', 'a/b;/c'),
]

OTHER_VALID_FILE_SPECS: Sequence[NameAndValue[List[FileSpecAbsStx]]] = [
    NameAndValue(
        'none',
        []),
    NameAndValue(
        'valid',
        [
            abs_stx.regular_file_spec(StringLiteralAbsStx('valid', QuoteType.HARD),
                                      abs_stx.FileContentsEmptyAbsStx())
        ]),
]


def file_type_and_contents_variants(file_name: StringAbsStx) -> Sequence[NameAndValue[FileSpecAbsStx]]:
    return [
        NameAndValue(
            'file_type={}, contents={}'.format(file_type, contents_variant.name),
            abs_stx.FileSpecAbsStx.of_file_type(file_type,
                                                file_name,
                                                contents_variant.value)
        )
        for file_type in defs.FileType
        for contents_variant in _CONTENTS_CASES[file_type]
    ]


_VALID_STRING_SOURCE = StringSourceOfStringAbsStx(StringLiteralAbsStx.empty_string())
_VALID_FILES_SOURCE = abs_stx.LiteralFilesSourceAbsStx(())

_CONTENTS_CASES: Mapping[FileType, Sequence[NameAndValue[ContentsAbsStx]]] = {
    defs.FileType.REGULAR: (
            [
                NameAndValue('empty', abs_stx.FileContentsEmptyAbsStx()),
            ] +
            [
                NameAndValue('explicit/{}'.format(mod),
                             abs_stx.FileContentsExplicitAbsStx(mod, _VALID_STRING_SOURCE))
                for mod in defs.ModificationType
            ]),
    defs.FileType.DIR: (
            [
                NameAndValue('empty', abs_stx.DirContentsEmptyAbsStx()),
            ] +
            [
                NameAndValue('explicit/{}'.format(mod),
                             abs_stx.DirContentsExplicitAbsStx(mod, _VALID_FILES_SOURCE))
                for mod in defs.ModificationType
            ])
}

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
