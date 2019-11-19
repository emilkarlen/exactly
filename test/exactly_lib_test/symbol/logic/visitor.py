import unittest
from typing import Sequence
from typing import Type

from exactly_lib.symbol.logic import visitor as sut
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import line_matcher, string_matcher, file_matcher, \
    files_matcher, string_transformer
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestVisitor)


class TestVisitor(unittest.TestCase):
    def _check(self,
               sdv_class: Type,
               sdv: sut.LogicTypeSdv,
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

    def test_visit_file_matcher(self):
        self._check(
            sut.FileMatcherSdv,
            file_matcher.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_files_matcher(self):
        self._check(
            sut.FilesMatcherSdv,
            files_matcher.arbitrary_sdv(),
            'other ret val',
        )

    def test_visit_line_matcher(self):
        self._check(
            sut.LineMatcherSdv,
            line_matcher.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_string_matcher(self):
        self._check(
            sut.StringMatcherSdv,
            string_matcher.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_string_transformer(self):
        self._check(
            sut.StringTransformerSdv,
            string_transformer.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_program(self):
        self._check(
            sut.ProgramSdv,
            program_sdvs.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_unknown_type(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(UnknownLogicTypeSdvClass())
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.LogicTypeSdvPseudoVisitor[str]):
    def __init__(self, ret_val: str):
        self._ret_val = ret_val
        self.visited_types = []

    def visit_file_matcher(self, value: sut.FileMatcherSdv) -> str:
        self.visited_types.append(sut.FileMatcherSdv)
        return self._ret_val

    def visit_files_matcher(self, value: sut.FilesMatcherSdv) -> str:
        self.visited_types.append(sut.FilesMatcherSdv)
        return self._ret_val

    def visit_line_matcher(self, value: sut.LineMatcherSdv) -> str:
        self.visited_types.append(sut.LineMatcherSdv)
        return self._ret_val

    def visit_string_matcher(self, value: sut.StringMatcherSdv) -> str:
        self.visited_types.append(sut.StringMatcherSdv)
        return self._ret_val

    def visit_string_transformer(self, value: sut.StringTransformerSdv) -> str:
        self.visited_types.append(sut.StringTransformerSdv)
        return self._ret_val

    def visit_program(self, value: sut.ProgramSdv) -> str:
        self.visited_types.append(sut.ProgramSdv)
        return self._ret_val


class UnknownLogicTypeSdvClass(sut.LogicTypeSdv):
    @property
    def logic_value_type(self) -> LogicValueType:
        raise NotImplementedError('unsupported')

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('unsupported')

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError('unsupported')

    def resolve(self, symbols: SymbolTable):
        raise NotImplementedError('unsupported')
