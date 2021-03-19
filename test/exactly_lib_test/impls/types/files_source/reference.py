import unittest
from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.files_source.test_resources import integration_check, models
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_fs
from exactly_lib_test.type_val_deps.types.files_source.test_resources.primitives import \
    FilesSourceThatWritesFileSystemElements
from exactly_lib_test.type_val_deps.types.files_source.test_resources.symbol_context import FilesSourceSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestReference(),
    ])


class TestReference(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        contents_cases: Sequence[NameAndValue[fs.FileSystemElements]] = [
            NameAndValue(
                'empty',
                (),
            ),
            NameAndValue(
                'non-empty',
                [fs.File.empty('empty-file.txt')],
            ),
        ]
        for contents_case in contents_cases:
            symbol = FilesSourceSymbolContext.of_primitive(
                'SYMBOL_NAME',
                FilesSourceThatWritesFileSystemElements(contents_case.value),
            )
            # ACT & ASSERT #
            integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
                self,
                symbol.abstract_syntax,
                models.empty(),
                arrangement_w_tcds(
                    symbols=symbol.symbol_table,
                ),
                MultiSourceExpectation(
                    symbol_references=symbol.references_assertion,
                    execution=ExecutionExpectation(
                        main_result=asrt_fs.dir_contains_exactly_2(contents_case.value)
                    )
                ),
                sub_test_identifiers={
                    'contents': contents_case.name,
                }
            )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
