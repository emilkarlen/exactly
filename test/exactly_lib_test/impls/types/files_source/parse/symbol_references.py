import unittest

from exactly_lib.impls.types.files_source.defs import FileType, ModificationType
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as abs_stx
from exactly_lib_test.impls.types.files_source.test_resources import integration_check
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import FileSpecAbsStx
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import LiteralFilesSourceAbsStx
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ExecutionExpectation, \
    MultiSourceExpectation
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_fs
from exactly_lib_test.type_val_deps.types.files_source.test_resources import references, primitives
from exactly_lib_test.type_val_deps.types.files_source.test_resources.symbol_context import FilesSourceSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_source.test_resources.symbol_context import \
    StringSourceSymbolContextOfPrimitiveConstant


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestAllSymbolReferencesAreReported(),
    ])


class TestAllSymbolReferencesAreReported(unittest.TestCase):
    def runTest(self):
        fn_f_1 = _fn_symbol('file__name__1', 'file-1.txt')
        fn_f_2 = _fn_symbol('file__name__2', 'file-2.txt')
        fn_f_3 = _fn_symbol('file__name__3', fn_f_2.str_value)
        fn_d_1 = _fn_symbol('dir__name__1', 'dir-1')
        fn_d_2 = _fn_symbol('dir__name__2', 'dir-2')
        fn_d_3 = _fn_symbol('dir__name__3', fn_d_2.str_value)

        contents_f_2 = StringSourceSymbolContextOfPrimitiveConstant('file_contents_2', 'contents of file 2')
        contents_f_3 = StringSourceSymbolContextOfPrimitiveConstant('file_contents_3', 'contents of file 3')

        contents_d_2 = FilesSourceSymbolContext.of_primitive('dir_contents_2',
                                                             primitives.FilesSourceThatDoesNothingTestImpl())
        contents_d_3 = FilesSourceSymbolContext.of_primitive('dir_contents_3',
                                                             primitives.FilesSourceThatDoesNothingTestImpl())

        expected_created_files = [
            fs.File.empty(fn_f_1.str_value),
            fs.File(fn_f_2.str_value, contents_f_2.contents_str + contents_f_3.contents_str),
            fs.Dir.empty(fn_d_1.str_value),
            fs.Dir.empty(fn_d_2.str_value),
        ]

        all_symbols = [
            fn_f_1,
            fn_f_2, contents_f_2,
            fn_f_3, contents_f_3,
            fn_d_1,
            fn_d_2, contents_d_2,
            fn_d_3, contents_d_3,
        ]
        syntax = LiteralFilesSourceAbsStx([
            _spec_regular(fn_f_1,
                          abs_stx.FileContentsEmptyAbsStx()),
            _spec_regular(fn_f_2,
                          abs_stx.FileContentsExplicitAbsStx(
                              ModificationType.CREATE,
                              contents_f_2.abstract_syntax,
                          )),
            _spec_regular(fn_f_3,
                          abs_stx.FileContentsExplicitAbsStx(
                              ModificationType.APPEND,
                              contents_f_3.abstract_syntax,
                          )),
            _spec_dir(fn_d_1,
                      abs_stx.DirContentsEmptyAbsStx()),
            _spec_dir(fn_d_2,
                      abs_stx.DirContentsExplicitAbsStx(
                          ModificationType.CREATE,
                          contents_d_2.abstract_syntax,
                      )),
            _spec_dir(fn_d_3,
                      abs_stx.DirContentsExplicitAbsStx(
                          ModificationType.APPEND,
                          contents_d_3.abstract_syntax,
                      )),
        ])
        # ACT & ASSERT #
        integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
            self,
            syntax,
            (),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(all_symbols)
            ),
            MultiSourceExpectation(
                symbol_references=SymbolContext.references_assertion_of_contexts(all_symbols),
                execution=ExecutionExpectation(
                    main_result=asrt_fs.dir_contains_exactly_2(
                        expected_created_files
                    )
                )
            )
        )


def _spec_regular(name: StringConstantSymbolContext,
                  contents: abs_stx.FileContentsAbsStx) -> FileSpecAbsStx:
    return FileSpecAbsStx(
        FileType.REGULAR,
        name.abstract_syntax,
        contents,
    )


def _spec_dir(name: StringConstantSymbolContext,
              contents: abs_stx.DirContentsAbsStx) -> FileSpecAbsStx:
    return FileSpecAbsStx(
        FileType.DIR,
        name.abstract_syntax,
        contents,
    )


def _fn_symbol(symbol_name, value: str) -> StringConstantSymbolContext:
    return StringConstantSymbolContext(
        symbol_name,
        value,
        default_restrictions=references.is_reference_restrictions_of_file_name_part()
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
