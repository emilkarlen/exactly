import unittest
from typing import Type

from exactly_lib.symbol.logic import visitor as sut
from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv, PRIMITIVE
from exactly_lib_test.symbol.test_resources import line_matcher, string_matcher, file_matcher, \
    files_matcher, string_transformer
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestVisitor)


class TestVisitor(unittest.TestCase):
    def _check(self,
               sdv_class: Type,
               sdv: sut.LogicTypeStv,
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
            sut.FileMatcherStv,
            file_matcher.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_files_matcher(self):
        self._check(
            sut.FilesMatcherStv,
            files_matcher.arbitrary_sdv(),
            'other ret val',
        )

    def test_visit_line_matcher(self):
        self._check(
            sut.LineMatcherStv,
            line_matcher.arbitrary_sdv(),
            'ret val',
        )

    def test_visit_string_matcher(self):
        self._check(
            sut.StringMatcherStv,
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
            visitor.visit(UnknownLogicTypeStvClass())
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.LogicTypeStvPseudoVisitor[str]):
    def __init__(self, ret_val: str):
        self._ret_val = ret_val
        self.visited_types = []

    def visit_file_matcher(self, value: sut.FileMatcherStv) -> str:
        self.visited_types.append(sut.FileMatcherStv)
        return self._ret_val

    def visit_files_matcher(self, value: sut.FilesMatcherStv) -> str:
        self.visited_types.append(sut.FilesMatcherStv)
        return self._ret_val

    def visit_line_matcher(self, value: sut.LineMatcherStv) -> str:
        self.visited_types.append(sut.LineMatcherStv)
        return self._ret_val

    def visit_string_matcher(self, value: sut.StringMatcherStv) -> str:
        self.visited_types.append(sut.StringMatcherStv)
        return self._ret_val

    def visit_string_transformer(self, value: sut.StringTransformerSdv) -> str:
        self.visited_types.append(sut.StringTransformerSdv)
        return self._ret_val

    def visit_program(self, value: sut.ProgramSdv) -> str:
        self.visited_types.append(sut.ProgramSdv)
        return self._ret_val


class UnknownLogicTypeStvClass(sut.LogicTypeStv):
    def value(self) -> LogicSdv[PRIMITIVE]:
        raise NotImplementedError('unsupported')
