import unittest
from typing import Sequence, Callable, TypeVar

from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependentValue
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.strings_ddvs import ConstantFragmentDdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources import test_of_test_resources_util
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.sym_ref.test_resources import sdv_assertions as sut
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import references as data_references
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.symbol_context import \
    LineMatcherSymbolValueContext
from exactly_lib_test.type_val_deps.types.path.test_resources.path_sdvs import \
    PathSdvTestImplWithConstantPathAndSymbolReferences
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import PathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext, \
    StringSymbolValueContext


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestMatchesSdv)


class TestMatchesSdv(unittest.TestCase):
    def test_fail_due_to_unexpected_sdv_type(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'unexpected logic type',
                LineMatcherSymbolValueContext.of_primitive_constant(False).sdv,
            ),
            NameAndValue(
                'data type',
                StringSymbolValueContext.of_constant('value').sdv,
            ),
        ]
        assertion = sut.matches_sdv(
            asrt.is_instance(ProgramSdv),
            asrt.anything_goes(),
            asrt.anything_goes())
        # ACT & ASSERT #
        for case in cases:
            with self.subTest(case.name):
                test_of_test_resources_util.assert_that_assertion_fails(assertion, case.value)

    def test_fail_due_to_unexpected_references(self):
        # ARRANGE #
        reference = data_references.reference_to__on_direct_and_indirect('symbol_name')
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
        path_symbol = PathDdvSymbolContext('symbol_name',
                                           path_ddvs.of_rel_option(RelOptionType.REL_ACT))
        reference = data_references.reference_to__on_direct_and_indirect(path_symbol.name)
        path_sdv = PathSdvTestImplWithConstantPathAndSymbolReferences(path_symbol.ddv,
                                                                      [reference])
        assertion = sut.matches_sdv(asrt.is_instance(PathSdv),
                                    asrt.len_equals(1),
                                    asrt.is_(path_symbol.ddv),
                                    asrt.is_(path_sdv),
                                    symbols=path_symbol.symbol_table)
        # ACT & ASSERT #
        assertion.apply_without_message(self, path_sdv)

    def test_symbol_table_is_passed_to_resolve_method(self):
        # ARRANGE #
        symbol_name = 'symbol_name'
        symbol_value = 'the symbol value'
        string_sdv = _StringSdvTestImpl(resolve_string_via_symbol_table(symbol_name))

        symbol_table = StringConstantSymbolContext(symbol_name, symbol_value).symbol_table
        is_expected_resolved_value = asrt.on_transformed(
            _resolve_ddv,
            asrt.equals(symbol_value)
        )
        assertion = sut.matches_sdv(asrt.anything_goes(),
                                    asrt.anything_goes(),
                                    is_expected_resolved_value,
                                    symbols=symbol_table)
        # ACT & ASSERT #
        assertion.apply_without_message(self, string_sdv)


def _resolve_ddv(ddv: DirDependentValue):
    return ddv.value_of_any_dependency(fake_tcds())


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
        assert container.value_type == ValueType.STRING, 'Value type must be STRING'
        return container.sdv.resolve(symbols)

    return ret_val


class _StringSdvTestImpl(DataTypeSdv):
    def __init__(self,
                 value_getter: Callable[[SymbolTable], StringDdv] = resolve_constant(STRING_DDV),
                 explicit_references: Sequence[SymbolReference] = ()):
        self.value_getter = value_getter
        self.explicit_references = explicit_references

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
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        raise NotImplementedError('not used')


class _ProgramResolverTestImpl(ProgramSdv):
    def __init__(self, explicit_references: Sequence[SymbolReference] = ()):
        self.explicit_references = explicit_references

    def new_accumulated(self, additional: AccumulatedComponents) -> '_ProgramResolverTestImpl':
        return _ProgramResolverTestImpl(self.explicit_references)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references

    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        raise NotImplementedError('not used')


class _StringTransformerSdvTestImpl(StringTransformerSdv):
    def __init__(self,
                 explicit_references: Sequence[SymbolReference] = ()):
        self.explicit_references = explicit_references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        raise NotImplementedError('not used')
