import unittest
from typing import Sequence

from exactly_lib.symbol.resolver_structure import DataValueResolver, LogicValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.concrete_string_values import ConstantFragment
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.value_type import ValueType, DataValueType, TypeCategory, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import resolver_assertions as sut
from exactly_lib_test.test_resources import test_of_test_resources_util
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsResolverOfDataType),
        unittest.makeSuite(TestIsResolverOfLogicType),
    ])


class TestIsResolverOfDataType(unittest.TestCase):
    def test_succeed(self):
        # ARRANGE #
        assertion = sut.is_resolver_of_data_type(DataValueType.STRING,
                                                 ValueType.STRING)
        matching_resolver = _StringResolverTestImpl('value')
        # ACT & ASSERT #
        assertion.apply_without_message(self, matching_resolver)

    def test_fail(self):
        # ARRANGE #
        assertion = sut.is_resolver_of_data_type(DataValueType.STRING,
                                                 ValueType.STRING)
        cases = [
            NameAndValue('unexpected data type',
                         _PathResolverTestImpl(),
                         ),
            NameAndValue('logic type',
                         _ProgramResolverTestImpl(),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                test_of_test_resources_util.assert_that_assertion_fails(assertion, case.value)


class TestIsResolverOfLogicType(unittest.TestCase):
    def test_succeed(self):
        # ARRANGE #
        assertion = sut.is_resolver_of_logic_type(LogicValueType.PROGRAM,
                                                  ValueType.PROGRAM)
        matching_resolver = _ProgramResolverTestImpl('value')
        # ACT & ASSERT #
        assertion.apply_without_message(self, matching_resolver)

    def test_fail(self):
        # ARRANGE #
        assertion = sut.is_resolver_of_logic_type(LogicValueType.PROGRAM,
                                                  ValueType.PROGRAM)
        cases = [
            NameAndValue('unexpected logic type',
                         _LinesTransformerResolverTestImpl(),
                         ),
            NameAndValue('data type',
                         _PathResolverTestImpl(),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                test_of_test_resources_util.assert_that_assertion_fails(assertion, case.value)


class _StringResolverTestImpl(DataValueResolver):
    def __init__(self,
                 value: str,
                 explicit_references: Sequence[SymbolReference] = ()):
        self.value = value
        self.explicit_references = explicit_references

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.DATA

    @property
    def data_value_type(self) -> DataValueType:
        return DataValueType.STRING

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING

    def resolve(self, symbols: SymbolTable) -> StringValue:
        return StringValue((ConstantFragment(self.value),))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references


class _PathResolverTestImpl(DataValueResolver):
    def __init__(self,
                 explicit_references: Sequence[SymbolReference] = ()):
        self.explicit_references = explicit_references

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.DATA

    @property
    def data_value_type(self) -> DataValueType:
        return DataValueType.PATH

    @property
    def value_type(self) -> ValueType:
        return ValueType.PATH

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references

    def resolve(self, symbols: SymbolTable) -> FileRef:
        raise NotImplementedError('not used')


class _ProgramResolverTestImpl(LogicValueResolver):
    def __init__(self,
                 explicit_references: Sequence[SymbolReference] = ()):
        self.explicit_references = explicit_references

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.LOGIC

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.PROGRAM

    @property
    def value_type(self) -> ValueType:
        return ValueType.PROGRAM

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references

    def resolve(self, symbols: SymbolTable) -> FileRef:
        raise NotImplementedError('not used')


class _LinesTransformerResolverTestImpl(LogicValueResolver):
    def __init__(self,
                 explicit_references: Sequence[SymbolReference] = ()):
        self.explicit_references = explicit_references

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.LOGIC

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.LINES_TRANSFORMER

    @property
    def value_type(self) -> ValueType:
        return ValueType.LINES_TRANSFORMER

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references

    def resolve(self, symbols: SymbolTable) -> FileRef:
        raise NotImplementedError('not used')
