import unittest

from exactly_lib.impls.types.files_source.impl import literal
from exactly_lib_test.impls.types.files_source.test_resources import integration_check, models
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_fs
from exactly_lib_test.type_val_deps.types.files_source.test_resources.symbol_context import FilesSourceSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEmpty(),
    ])


class TestEmpty(unittest.TestCase):
    def runTest(self):
        symbol = FilesSourceSymbolContext.of_primitive(
            'SYMBOL_NAME',
            literal.Literal(()),
        )
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
                    main_result=asrt_fs.dir_contains_exactly_2(())
                )
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
