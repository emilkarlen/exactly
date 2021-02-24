from typing import Sequence, Optional, Callable

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol import value_type
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue, ReferenceRestrictions, \
    SymbolContainer
from exactly_lib.symbol.value_type import WithStrRenderingType, ValueType
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION, SymbolContext
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.full_deps.symbol_context import LogicSymbolValueContext, \
    LogicTypeSymbolContext
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_context import DataSymbolValueContext, \
    DataTypeSymbolContext


class DataTypeSdvForTest(DataTypeSdv):
    def __init__(self, references: Sequence[SymbolReference]):
        self._references = references

    def resolve(self, symbols: SymbolTable):
        raise NotImplementedError('It is an error if this method is called')

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class FullDepsSdvForTest(FullDepsSdv):
    def __init__(self, references: Sequence[SymbolReference]):
        self._references = references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FullDepsDdv:
        raise NotImplementedError('It is an error if this method is called')


class TestDataSymbolValueContext(DataSymbolValueContext[DataTypeSdvForTest]):
    def __init__(self,
                 sdv: DataTypeSdvForTest,
                 data_value_type: WithStrRenderingType,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)
        self._data_value_type = data_value_type
        self._value_type = value_type.W_STR_RENDERING_TYPE_2_VALUE_TYPE[data_value_type]

    @staticmethod
    def of(references: Sequence[SymbolReference],
           data_value_type: WithStrRenderingType,
           definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
           ) -> 'TestDataSymbolValueContext':
        return TestDataSymbolValueContext(DataTypeSdvForTest(references),
                                          data_value_type,
                                          definition_source)

    @property
    def value_type(self) -> ValueType:
        return self._value_type

    @property
    def assert_equals_sdv(self) -> Assertion[SymbolDependentValue]:
        raise NotImplementedError('unsupported')

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        raise NotImplementedError('unsupported')


class TestDataSymbolContext(DataTypeSymbolContext[DataTypeSdvForTest]):
    def __init__(self,
                 name: str,
                 value: TestDataSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of(symbol_name: str,
           references: Sequence[SymbolReference],
           value_type: WithStrRenderingType = WithStrRenderingType.STRING,
           definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
           ) -> 'TestDataSymbolContext':
        return TestDataSymbolContext(symbol_name,
                                     TestDataSymbolValueContext.of(references, value_type, definition_source))

    @property
    def value(self) -> TestDataSymbolValueContext:
        return self._value


class TestLogicSymbolValueContext(LogicSymbolValueContext[FullDepsSdvForTest]):
    def __init__(self,
                 sdv: FullDepsSdvForTest,
                 logic_value_type: ValueType,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)
        self._value_type = logic_value_type

    @staticmethod
    def of(references: Sequence[SymbolReference],
           logic_value_type: ValueType,
           definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
           ) -> 'TestLogicSymbolValueContext':
        return TestLogicSymbolValueContext(FullDepsSdvForTest(references),
                                           logic_value_type,
                                           definition_source)

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        raise NotImplementedError('unsupported')

    @property
    def value_type(self) -> ValueType:
        return self._value_type


class TestLogicSymbolContext(LogicTypeSymbolContext[FullDepsSdvForTest]):
    def __init__(self,
                 name: str,
                 value: TestLogicSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of(symbol_name: str,
           references: Sequence[SymbolReference],
           value_type: ValueType = ValueType.FILE_MATCHER,
           definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
           ) -> 'TestLogicSymbolContext':
        return TestLogicSymbolContext(symbol_name,
                                      TestLogicSymbolValueContext.of(references, value_type, definition_source))

    @property
    def value(self) -> TestLogicSymbolValueContext:
        return self._value

    @property
    def reference_sdv(self) -> FullDepsSdvForTest:
        raise NotImplementedError('unsupported')

    @property
    def abstract_syntax(self) -> AbstractSyntax:
        raise NotImplementedError('unsupported')


def reference_to(symbol: SymbolContext, restrictions: ReferenceRestrictions) -> SymbolReference:
    return SymbolReference(symbol.name, restrictions)


def unconditional_satisfaction(value: SymbolContainer) -> Optional[str]:
    return None


def unconditional_dissatisfaction(result: str) -> Callable[[SymbolContainer], Optional[str]]:
    def ret_val(value: SymbolContainer) -> str:
        return result

    return ret_val


def dissatisfaction_if_value_type_is(value_type: ValueType) -> Callable[[SymbolContainer], Optional[str]]:
    def ret_val(container: SymbolContainer) -> Optional[str]:
        if container.value_type is value_type:
            return 'fail due to value type is ' + str(value_type)
        return None

    return ret_val
