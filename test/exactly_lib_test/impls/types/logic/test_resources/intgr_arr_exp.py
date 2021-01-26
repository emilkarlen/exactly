from typing import Optional, Sequence, Generic, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.tcfs.test_resources import tcds_populators, hds_populators, non_hds_populator
from exactly_lib_test.tcfs.test_resources.ds_action import PlainTcdsAction
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducer
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.common_properties_checker import OUTPUT, \
    PRIMITIVE


class Arrangement:
    def __init__(self,
                 symbols: Optional[SymbolTable] = None,
                 tcds: Optional[TcdsArrangement] = None,
                 process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement(),
                 mem_buff_size: int = 2 ** 10,
                 ):
        """
        :param tcds: Not None iff TCDS is used (and must thus be created)
        """
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.tcds = tcds
        self.process_execution = process_execution
        self.mem_buff_size = mem_buff_size


def arrangement_w_tcds(tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                       hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                       non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                       act_result: Optional[ActResultProducer] = None,
                       pre_population_action: PlainTcdsAction = PlainTcdsAction(),
                       post_population_action: PlainTcdsAction = PlainTcdsAction(),
                       symbols: Optional[SymbolTable] = None,
                       process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement(),
                       ) -> Arrangement:
    """
    :return: An Arrangement with will create a TCDS
    """
    tcds = TcdsArrangement(
        hds_contents=hds_contents,
        non_hds_contents=non_hds_contents,
        tcds_contents=tcds_contents,
        act_result=act_result,
        pre_population_action=pre_population_action,
        post_population_action=post_population_action,
    )
    return Arrangement(symbols,
                       tcds,
                       process_execution)


def arrangement_wo_tcds(symbols: Optional[SymbolTable] = None,
                        process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement(),
                        ) -> Arrangement:
    """
    :return: An Arrangement with will NOT create a TCDS
    """
    return Arrangement(symbols,
                       None,
                       process_execution)


class ParseExpectation:
    """Expected properties after parse."""

    def __init__(
            self,
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
            symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
    ):
        self.source = source
        self.symbol_references = symbol_references


class ExecutionExpectation(Generic[OUTPUT]):
    def __init__(
            self,
            validation: ValidationAssertions = ValidationAssertions.all_passes(),
            main_result: ValueAssertion[OUTPUT] = asrt.anything_goes(),
            is_hard_error: Optional[ValueAssertion[TextRenderer]] = None,
    ):
        self.validation = validation
        self.main_result = main_result
        self.is_hard_error = is_hard_error


class AssertionResolvingEnvironment:
    def __init__(self,
                 tcds: TestCaseDs,
                 app_env: ApplicationEnvironment,
                 ):
        self.tcds = tcds
        self.app_env = app_env


MkAdvAssertion = Callable[
    [AssertionResolvingEnvironment],
    ValueAssertion[ApplicationEnvironmentDependentValue]
]


def prim_asrt__any(environment: AssertionResolvingEnvironment) -> ValueAssertion:
    return asrt.anything_goes()


def adv_asrt__any(environment: AssertionResolvingEnvironment) -> ValueAssertion[ApplicationEnvironmentDependentValue]:
    return asrt.anything_goes()


def prim_asrt__constant(primitive: ValueAssertion[PRIMITIVE]
                        ) -> Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]]:
    def ret_val(environment: AssertionResolvingEnvironment) -> ValueAssertion[PRIMITIVE]:
        return primitive

    return ret_val


def adv_asrt__constant(adv: ValueAssertion[ApplicationEnvironmentDependentValue[PRIMITIVE]]
                       ) -> MkAdvAssertion:
    def ret_val(environment: AssertionResolvingEnvironment,
                ) -> ValueAssertion[ApplicationEnvironmentDependentValue[PRIMITIVE]]:
        return adv

    return ret_val


class PrimAndExeExpectation(Generic[PRIMITIVE, OUTPUT]):
    def __init__(
            self,
            execution: ExecutionExpectation[OUTPUT] = ExecutionExpectation(),
            primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]] = prim_asrt__any,
            adv: Callable[[AssertionResolvingEnvironment],
                          ValueAssertion[ApplicationEnvironmentDependentValue[PRIMITIVE]]] = adv_asrt__any,
    ):
        self.execution = execution
        self.primitive = primitive
        self.adv = adv

    @staticmethod
    def of_exe(
            validation: ValidationAssertions = ValidationAssertions.all_passes(),
            main_result: ValueAssertion[OUTPUT] = asrt.anything_goes(),
            is_hard_error: Optional[ValueAssertion[TextRenderer]] = None,
    ) -> 'PrimAndExeExpectation[PRIMITIVE, OUTPUT]':
        return PrimAndExeExpectation(
            ExecutionExpectation(
                validation=validation,
                main_result=main_result,
                is_hard_error=is_hard_error,
            ),
            prim_asrt__any,
        )

    @staticmethod
    def of_prim(
            primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]] = prim_asrt__any,
    ) -> 'PrimAndExeExpectation[PRIMITIVE, OUTPUT]':
        return PrimAndExeExpectation(
            ExecutionExpectation(),
            primitive
        )

    @staticmethod
    def of_prim__const(
            primitive: ValueAssertion[PRIMITIVE] = prim_asrt__any,
    ) -> 'PrimAndExeExpectation[PRIMITIVE, OUTPUT]':
        return PrimAndExeExpectation(
            ExecutionExpectation(),
            prim_asrt__constant(primitive)
        )


class Expectation(Generic[PRIMITIVE, OUTPUT]):
    def __init__(
            self,
            parse: ParseExpectation = ParseExpectation(),
            execution: ExecutionExpectation[OUTPUT] = ExecutionExpectation(),
            primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]] = prim_asrt__any,
            adv: MkAdvAssertion = adv_asrt__any,
    ):
        """
        :param primitive: Expectation of custom properties of the primitive object,
        i.e. properties other than the standard execution properties.
        """
        self.parse = parse
        self.execution = execution
        self.primitive = primitive
        self.adv = adv

    @staticmethod
    def of_prim(primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]],
                parse: ParseExpectation = ParseExpectation(),
                ) -> 'Expectation':
        return Expectation(parse=parse,
                           primitive=primitive)

    @staticmethod
    def of_prim__const(primitive: ValueAssertion[PRIMITIVE],
                       parse: ParseExpectation = ParseExpectation(),
                       ) -> 'Expectation':
        return Expectation.of_prim(lambda env: primitive, parse)

    @property
    def prim_and_exe(self) -> PrimAndExeExpectation[PRIMITIVE, OUTPUT]:
        return PrimAndExeExpectation(
            self.execution,
            self.primitive,
            self.adv,
        )


class MultiSourceExpectation(Generic[PRIMITIVE, OUTPUT]):
    def __init__(
            self,
            symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
            execution: ExecutionExpectation[OUTPUT] = ExecutionExpectation(),
            primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]] = prim_asrt__any,
            adv: MkAdvAssertion = adv_asrt__any,
    ):
        self.symbol_references = symbol_references
        self.execution = execution
        self.primitive = primitive
        self.adv = adv

    @staticmethod
    def of_const(
            symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
            execution: ExecutionExpectation[OUTPUT] = ExecutionExpectation(),
            primitive: ValueAssertion[PRIMITIVE] = asrt.anything_goes(),
            adv: ValueAssertion[ApplicationEnvironmentDependentValue[PRIMITIVE]] = asrt.anything_goes(),
    ) -> 'MultiSourceExpectation':
        return MultiSourceExpectation(
            symbol_references,
            execution,
            prim_asrt__constant(primitive),
            adv_asrt__constant(adv),
        )

    @staticmethod
    def of_prim(primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]],
                symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                ) -> 'MultiSourceExpectation':
        return MultiSourceExpectation(symbol_references=symbol_references,
                                      primitive=primitive)

    @staticmethod
    def of_prim__const(primitive: ValueAssertion[PRIMITIVE],
                       symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                       ) -> 'MultiSourceExpectation':
        return MultiSourceExpectation.of_prim(lambda env: primitive, symbol_references)

    @property
    def prim_and_exe(self) -> PrimAndExeExpectation[PRIMITIVE, OUTPUT]:
        return PrimAndExeExpectation(
            self.execution,
            self.primitive
        )
