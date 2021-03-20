import unittest
from typing import Sequence, Tuple

from exactly_lib.impls.types.files_source import syntax
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as abs_stx
from exactly_lib_test.impls.types.files_source.test_resources import integration_check
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import LiteralFilesSourceAbsStx, \
    FileSpecAbsStx
from exactly_lib_test.symbol.test_resources.symbol_syntax import A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInvalidDelimiters(),
        TestMissingContents(),
        TestInvalidModificationToken(),
        TestInvalidFileType(),
    ])


class TestInvalidDelimiters(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        valid_file_specs_cases: Sequence[NameAndValue[Sequence[FileSpecAbsStx]]] = [
            NameAndValue(
                'none',
                (),
            ),
            NameAndValue(
                'single valid',
                [abs_stx.regular_file_spec__str_name('valid_file_name',
                                                     abs_stx.FileContentsEmptyAbsStx())],
            ),
        ]
        invalid_delimiters_cases: Sequence[NameAndValue[Tuple[str, str]]] = [
            NameAndValue(
                'start missing',
                ('', syntax.FILE_LIST_END),
            ),
            NameAndValue(
                'start is end',
                (syntax.FILE_LIST_END, syntax.FILE_LIST_END),
            ),
            NameAndValue(
                'end missing',
                (syntax.FILE_LIST_BEGIN, ''),
            ),
            NameAndValue(
                'end is start',
                (syntax.FILE_LIST_BEGIN, syntax.FILE_LIST_BEGIN),
            ),
        ]
        for valid_file_specs_case in valid_file_specs_cases:
            for invalid_delimiters_case in invalid_delimiters_cases:
                # ACT & ASSERT #
                integration_check.PARSE_CHECKER__FULL.check_invalid_syntax__abs_stx(
                    self,
                    LiteralFilesSourceAbsStx(valid_file_specs_case.value,
                                             delimiter__begin=invalid_delimiters_case.value[0],
                                             delimiter__end=invalid_delimiters_case.value[1],
                                             ),
                    sub_test_identifiers={
                        'file_specs': valid_file_specs_case.name,
                        'delimiters': invalid_delimiters_case.name,
                    }
                )


class TestMissingContents(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for modification_type in abs_stx.ModificationType:
            for file_type in abs_stx.FileType:
                missing_contents_file_spec = abs_stx.FileSpecAbsStx.of_file_type(
                    file_type,
                    StringLiteralAbsStx('valid_file_name'),
                    abs_stx.CustomContentsAbsStx(
                        abs_stx.ContentsAbsStx.of_modification_type(
                            modification_type,
                            CustomAbsStx.empty(),
                        ),
                    )
                )
                literal_syntax = abs_stx.LiteralFilesSourceAbsStx([missing_contents_file_spec])
                # ACT & ASSERT #
                integration_check.PARSE_CHECKER__FULL.check_invalid_syntax__abs_stx(
                    self,
                    literal_syntax,
                    sub_test_identifiers={
                        'modification_type': modification_type,
                        'file_type': file_type,
                    }
                )


class TestInvalidModificationToken(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        invalid_modification_types = [':',
                                      2 * syntax.EXPLICIT_CREATE,
                                      'text']

        for invalid_modification_type in invalid_modification_types:
            for file_type in abs_stx.FileType:
                missing_contents_file_spec = abs_stx.FileSpecAbsStx.of_file_type(
                    file_type,
                    StringLiteralAbsStx('valid_file_name'),
                    abs_stx.CustomContentsAbsStx(
                        abs_stx.ContentsAbsStx.of_modification(
                            TokenSequence.singleton(invalid_modification_type),
                            CustomAbsStx.singleton(A_VALID_SYMBOL_NAME),
                        ),
                    )
                )
                literal_syntax = abs_stx.LiteralFilesSourceAbsStx([missing_contents_file_spec])
                # ACT & ASSERT #
                integration_check.PARSE_CHECKER__FULL.check_invalid_syntax__abs_stx(
                    self,
                    literal_syntax,
                    sub_test_identifiers={
                        'file_type': file_type,
                        'invalid_modification_type': invalid_modification_type,
                    }
                )


class TestInvalidFileType(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        missing_contents_file_spec = abs_stx.FileSpecAbsStx(
            'invalid_file_type_token',
            StringLiteralAbsStx('valid_file_name'),
            abs_stx.FileContentsEmptyAbsStx()
        )
        literal_syntax = abs_stx.LiteralFilesSourceAbsStx([missing_contents_file_spec])
        # ACT & ASSERT #
        integration_check.PARSE_CHECKER__FULL.check_invalid_syntax__abs_stx(
            self,
            literal_syntax,
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
