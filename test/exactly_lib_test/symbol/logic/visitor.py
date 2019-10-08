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
from exactly_lib_test.test_case_utils.program.test_resources import program_resolvers


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestVisitor)


class TestVisitor(unittest.TestCase):
    def _check(self,
               resolver_class: Type,
               resolver: sut.LogicValueResolver,
               expected_ret_val: str,
               ):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods(expected_ret_val)

        actual_ret_val = visitor.visit(resolver)

        # ASSERT #

        self.assertEqual(expected_ret_val,
                         actual_ret_val,
                         'return value')

        self.assertEqual([resolver_class],
                         visitor.visited_types,
                         'visited classes')

    def test_visit_file_matcher(self):
        self._check(
            sut.FileMatcherResolver,
            file_matcher.arbitrary_resolver(),
            'ret val',
        )

    def test_visit_files_matcher(self):
        self._check(
            sut.FilesMatcherResolver,
            files_matcher.arbitrary_resolver(),
            'other ret val',
        )

    def test_visit_line_matcher(self):
        self._check(
            sut.LineMatcherResolver,
            line_matcher.arbitrary_resolver(),
            'ret val',
        )

    def test_visit_string_matcher(self):
        self._check(
            sut.StringMatcherResolver,
            string_matcher.arbitrary_resolver(),
            'ret val',
        )

    def test_visit_string_transformer(self):
        self._check(
            sut.StringTransformerResolver,
            string_transformer.arbitrary_resolver(),
            'ret val',
        )

    def test_visit_program(self):
        self._check(
            sut.ProgramResolver,
            program_resolvers.arbitrary_resolver(),
            'ret val',
        )

    def test_visit_unknown_type(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(UnknownLogicTypeResolverClass())
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.LogicValueResolverPseudoVisitor[str]):
    def __init__(self, ret_val: str):
        self._ret_val = ret_val
        self.visited_types = []

    def visit_file_matcher(self, value: sut.FileMatcherResolver) -> str:
        self.visited_types.append(sut.FileMatcherResolver)
        return self._ret_val

    def visit_files_matcher(self, value: sut.FilesMatcherResolver) -> str:
        self.visited_types.append(sut.FilesMatcherResolver)
        return self._ret_val

    def visit_line_matcher(self, value: sut.LineMatcherResolver) -> str:
        self.visited_types.append(sut.LineMatcherResolver)
        return self._ret_val

    def visit_string_matcher(self, value: sut.StringMatcherResolver) -> str:
        self.visited_types.append(sut.StringMatcherResolver)
        return self._ret_val

    def visit_string_transformer(self, value: sut.StringTransformerResolver) -> str:
        self.visited_types.append(sut.StringTransformerResolver)
        return self._ret_val

    def visit_program(self, value: sut.ProgramResolver) -> str:
        self.visited_types.append(sut.ProgramResolver)
        return self._ret_val


class UnknownLogicTypeResolverClass(sut.LogicValueResolver):
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
