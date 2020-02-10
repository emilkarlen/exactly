import unittest
from typing import Sequence, Callable, TypeVar

from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.type_system.data.concrete_strings import ConstantFragmentDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.type_system.value_type import ValueType, DataValueType, TypeCategory, LogicValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable, singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import sdv_assertions as sut
from exactly_lib_test.symbol.test_resources import sdv_structure_assertions as asrt_sdv_struct
from exactly_lib_test.test_resources import test_of_test_resources_util
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
        assertion = sut.is_sdv_of_data_type(DataValueType.STRING,
                                            ValueType.STRING)
        matching_sdv = _StringSdvTestImpl()
        # ACT & ASSERT #
        assertion.apply_without_message(self, matching_sdv)

    def test_fail(self):
        # ARRANGE #
        assertion = sut.is_sdv_of_data_type(DataValueType.STRING,
                                            ValueType.STRING)
        cases = [
            NameAndValue('unexpected data type',
                         _PathSdvTestImpl(),
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
        assertion = asrt_sdv_struct.is_sdv_of_logic_type(LogicValueType.PROGRAM)
        matching_sdv = _ProgramResolverTestImpl()
        # ACT & ASSERT #
        assertion.apply_without_message(self, matching_sdv)

    def test_fail(self):
        # ARRANGE #
        assertion = asrt_sdv_struct.is_sdv_of_logic_type(LogicValueType.PROGRAM)
        cases = [
            NameAndValue('unexpected logic type',
                         _StringTransformerSdvTestImpl(),
                         ),
            NameAndValue('data type',
                         _PathSdvTestImpl(),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                test_of_test_resources_util.assert_that_assertion_fails(assertion, case.value)


class TestMatchesResolver(unittest.TestCase):
    def test_fail_due_to_unexpected_sdv_type(self):
        # ARRANGE #
        string_sdv = _StringSdvTestImpl()
        assertion = sut.matches_sdv(
            asrt_sdv_struct.is_sdv_of_logic_type(LogicValueType.PROGRAM),
            asrt.anything_goes(),
            asrt.anything_goes())
        # ACT & ASSERT #
        test_of_test_resources_util.assert_that_assertion_fails(assertion, string_sdv)

    def test_fail_due_to_unexpected_references(self):
        # ARRANGE #
        reference = data_symbol_utils.symbol_reference('symbol_name')
        string_sdv_with_single_reference = _StringSdvTestImpl(explicit_references=[reference])

        assertion = sut.matches_sdv(asrt.anything_goes(),
                                    asrt.is_empty_sequence,
                                    asrt.anything_goes())
        # ACT & ASSERT #
        test_of_test_resources_util.assert_that_assertion_fails(
            assertion,
            string_sdv_with_single_reference)

    def test_fail_due_to_unexpected_resolved_value(self):
        # ARRANGE #
        string_sdv = _StringSdvTestImpl(resolve_constant(STRING_DDV))
        assertion = sut.matches_sdv(asrt.anything_goes(),
                                    asrt.anything_goes(),
                                    asrt.not_(asrt.is_(STRING_DDV)))
        # ACT & ASSERT #
        test_of_test_resources_util.assert_that_assertion_fails(assertion, string_sdv)

    def test_fail_due_to_failing_custom_assertion(self):
        # ARRANGE #
        string_sdv = _StringSdvTestImpl(resolve_constant(STRING_DDV))
        assertion = sut.matches_sdv(asrt.anything_goes(),
                                    asrt.anything_goes(),
                                    asrt.anything_goes(),
                                    asrt.not_(asrt.is_(string_sdv)))
        # ACT & ASSERT #
        test_of_test_resources_util.assert_that_assertion_fails(assertion, string_sdv)

    def test_success(self):
        # ARRANGE #
        reference = data_symbol_utils.symbol_reference('symbol_name')
        string_sdv = _StringSdvTestImpl(resolve_constant(STRING_DDV), [reference])
        assertion = sut.matches_sdv(sut.is_sdv_of_string_type(),
                                    asrt.len_equals(1),
                                    asrt.is_(STRING_DDV),
                                    asrt.is_(string_sdv))
        # ACT & ASSERT #
        assertion.apply_without_message(self, string_sdv)

    def test_symbol_table_is_passed_to_resolve_method(self):
        # ARRANGE #
        symbol_name = 'symbol_name'
        string_sdv = _StringSdvTestImpl(resolve_string_via_symbol_table(symbol_name))
        symbol_table = singleton_symbol_table_2(symbol_name,
                                                data_symbol_utils.string_ddv_constant_container2(STRING_DDV))

        assertion = sut.matches_sdv(asrt.anything_goes(),
                                    asrt.anything_goes(),
                                    asrt.is_(STRING_DDV),
                                    symbols=symbol_table)
        # ACT & ASSERT #
        assertion.apply_without_message(self, string_sdv)


STRING_DDV = StringDdv((ConstantFragmentDdv('value'),))

T = TypeVar('T')


def resolve_constant(constant: T) -> Callable[[SymbolTable], T]:
    def ret_val(symbols: SymbolTable) -> T:
        return constant

    return ret_val


def resolve_string_via_symbol_table(symbol_name: str) -> Callable[[SymbolTable], StringDdv]:
    def ret_val(symbols: SymbolTable) -> StringDdv:
        container = symbols.lookup(symbol_name)
        assert isinstance(container, SymbolContainer), 'Value in Symbol Table must be SymbolContainer'
        return container.sdv.resolve(symbols)

    return ret_val


class _StringSdvTestImpl(DataTypeSdv):
    def __init__(self,
                 value_getter: Callable[[SymbolTable], StringDdv] = resolve_constant(STRING_DDV),
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

    def resolve(self, symbols: SymbolTable) -> StringDdv:
        return self.value_getter(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references


class _PathSdvTestImpl(DataTypeSdv):
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

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        raise NotImplementedError('not used')


class _ProgramResolverTestImpl(LogicTypeSdv):
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

    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        raise NotImplementedError('not used')


class _StringTransformerSdvTestImpl(LogicTypeSdv):
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

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        raise NotImplementedError('not used')
