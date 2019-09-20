import unittest
from typing import Sequence, Callable, TypeVar

from exactly_lib.symbol.data.data_value_resolver import DataValueResolver
from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.concrete_string_values import ConstantFragment
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.logic.program.program_value import ProgramValue
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue
from exactly_lib.type_system.value_type import ValueType, DataValueType, TypeCategory, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable, singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import resolver_assertions as sut
from exactly_lib_test.test_resources import test_of_test_resources_util
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsResolverOfDataType),
        unittest.makeSuite(TestIsResolverOfLogicType),
        unittest.makeSuite(TestMatchesResolver),
    ])


class TestIsResolverOfDataType(unittest.TestCase):
    def test_succeed(self):
        # ARRANGE #
        assertion = sut.is_resolver_of_data_type(DataValueType.STRING,
                                                 ValueType.STRING)
        matching_resolver = _StringResolverTestImpl()
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
        matching_resolver = _ProgramResolverTestImpl()
        # ACT & ASSERT #
        assertion.apply_without_message(self, matching_resolver)

    def test_fail(self):
        # ARRANGE #
        assertion = sut.is_resolver_of_logic_type(LogicValueType.PROGRAM,
                                                  ValueType.PROGRAM)
        cases = [
            NameAndValue('unexpected logic type',
                         _StringTransformerResolverTestImpl(),
                         ),
            NameAndValue('data type',
                         _PathResolverTestImpl(),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                test_of_test_resources_util.assert_that_assertion_fails(assertion, case.value)


class TestMatchesResolver(unittest.TestCase):
    def test_fail_due_to_unexpected_resolver_type(self):
        # ARRANGE #
        string_resolver = _StringResolverTestImpl()
        assertion = sut.matches_resolver(sut.is_resolver_of_logic_type(LogicValueType.PROGRAM,
                                                                       ValueType.PROGRAM),
                                         asrt.anything_goes(),
                                         asrt.anything_goes())
        # ACT & ASSERT #
        test_of_test_resources_util.assert_that_assertion_fails(assertion, string_resolver)

    def test_fail_due_to_unexpected_references(self):
        # ARRANGE #
        reference = data_symbol_utils.symbol_reference('symbol_name')
        string_resolver_with_single_reference = _StringResolverTestImpl(explicit_references=[reference])

        assertion = sut.matches_resolver(asrt.anything_goes(),
                                         asrt.is_empty_sequence,
                                         asrt.anything_goes())
        # ACT & ASSERT #
        test_of_test_resources_util.assert_that_assertion_fails(
            assertion,
            string_resolver_with_single_reference)

    def test_fail_due_to_unexpected_resolved_value(self):
        # ARRANGE #
        string_resolver = _StringResolverTestImpl(resolve_constant(STRING_VALUE))
        assertion = sut.matches_resolver(asrt.anything_goes(),
                                         asrt.anything_goes(),
                                         asrt.not_(asrt.is_(STRING_VALUE)))
        # ACT & ASSERT #
        test_of_test_resources_util.assert_that_assertion_fails(assertion, string_resolver)

    def test_fail_due_to_failing_custom_assertion(self):
        # ARRANGE #
        string_resolver = _StringResolverTestImpl(resolve_constant(STRING_VALUE))
        assertion = sut.matches_resolver(asrt.anything_goes(),
                                         asrt.anything_goes(),
                                         asrt.anything_goes(),
                                         asrt.not_(asrt.is_(string_resolver)))
        # ACT & ASSERT #
        test_of_test_resources_util.assert_that_assertion_fails(assertion, string_resolver)

    def test_success(self):
        # ARRANGE #
        reference = data_symbol_utils.symbol_reference('symbol_name')
        string_resolver = _StringResolverTestImpl(resolve_constant(STRING_VALUE), [reference])
        assertion = sut.matches_resolver(sut.is_resolver_of_string_type(),
                                         asrt.len_equals(1),
                                         asrt.is_(STRING_VALUE),
                                         asrt.is_(string_resolver))
        # ACT & ASSERT #
        assertion.apply_without_message(self, string_resolver)

    def test_symbol_table_is_passed_to_resolve_method(self):
        # ARRANGE #
        symbol_name = 'symbol_name'
        string_resolver = _StringResolverTestImpl(resolve_string_via_symbol_table(symbol_name))
        symbol_table = singleton_symbol_table_2(symbol_name,
                                                data_symbol_utils.string_value_constant_container2(STRING_VALUE))

        assertion = sut.matches_resolver(asrt.anything_goes(),
                                         asrt.anything_goes(),
                                         asrt.is_(STRING_VALUE),
                                         symbols=symbol_table)
        # ACT & ASSERT #
        assertion.apply_without_message(self, string_resolver)


STRING_VALUE = StringValue((ConstantFragment('value'),))

T = TypeVar('T')


def resolve_constant(constant: T) -> Callable[[SymbolTable], T]:
    def ret_val(symbols: SymbolTable) -> T:
        return constant

    return ret_val


def resolve_string_via_symbol_table(symbol_name: str) -> Callable[[SymbolTable], StringValue]:
    def ret_val(symbols: SymbolTable) -> StringValue:
        container = symbols.lookup(symbol_name)
        assert isinstance(container, SymbolContainer), 'Value in SymTbl must be SymbolContainer'
        return container.resolver.resolve(symbols)

    return ret_val


class _StringResolverTestImpl(DataValueResolver):
    def __init__(self,
                 value_getter: Callable[[SymbolTable], StringValue] = resolve_constant(STRING_VALUE),
                 explicit_references: Sequence[SymbolReference] = ()):
        self.value_getter = value_getter
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
        return self.value_getter(symbols)

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

    def resolve(self, symbols: SymbolTable) -> ProgramValue:
        raise NotImplementedError('not used')


class _StringTransformerResolverTestImpl(LogicValueResolver):
    def __init__(self,
                 explicit_references: Sequence[SymbolReference] = ()):
        self.explicit_references = explicit_references

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.LOGIC

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.STRING_TRANSFORMER

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_TRANSFORMER

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        raise NotImplementedError('not used')
