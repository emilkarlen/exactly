import unittest
from typing import List
from typing import Type

from exactly_lib.symbol.data import visitor as sut
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.dir_dependent_value import DependenciesAwareDdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.test_resources import string_sdvs, list_sdvs, path_sdvs


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestVisitor)


class TestVisitor(unittest.TestCase):
    def _check(self,
               sdv_class: Type,
               sdv: sut.DataTypeSdv,
               expected_ret_val: str,
               ):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods(expected_ret_val)

        actual_ret_val = visitor.visit(sdv)

        # ASSERT #

        self.assertEqual(expected_ret_val,
                         actual_ret_val,
                         'return value')

        self.assertEqual([sdv_class],
                         visitor.visited_types,
                         'visited classes')

    def test_visit_string(self):
        self._check(
            sut.StringSdv,
            string_sdvs.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_path(self):
        self._check(
            sut.PathSdv,
            path_sdvs.arbitrary_sdv(),
            'other ret val',
        )

    def test_visit_list(self):
        self._check(
            sut.ListSdv,
            list_sdvs.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_unknown_type(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(UnknownDataTypeSdvClass())
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.DataTypeSdvPseudoVisitor[str]):
    def __init__(self, ret_val: str):
        self._ret_val = ret_val
        self.visited_types = []

    def visit_string(self, value: sut.StringSdv) -> str:
        self.visited_types.append(sut.StringSdv)
        return self._ret_val

    def visit_path(self, value: sut.PathSdv) -> str:
        self.visited_types.append(sut.PathSdv)
        return self._ret_val

    def visit_list(self, value: sut.ListSdv) -> str:
        self.visited_types.append(sut.ListSdv)
        return self._ret_val


class UnknownDataTypeSdvClass(sut.DataTypeSdv):
    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('unsupported')

    def resolve(self, symbols: SymbolTable) -> DependenciesAwareDdv:
        raise NotImplementedError('unsupported')
