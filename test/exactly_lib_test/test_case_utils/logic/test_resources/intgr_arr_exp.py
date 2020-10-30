from typing import Optional, Sequence, Generic, Callable

from exactly_lib.appl_env.application_environment import ApplicationEnvironment
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.tcfs.test_resources import tcds_populators, hds_populators, non_hds_populator
from exactly_lib_test.tcfs.test_resources.ds_action import PlainTcdsAction
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducer
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import OUTPUT, PRIMITIVE
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationAssertions, all_validations_passes
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Arrangement:
    def __init__(self,
                 symbols: Optional[SymbolTable] = None,
                 tcds: Optional[TcdsArrangement] = None,
                 process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement()
                 ):
        """
        :param tcds: Not None iff TCDS is used (and must thus be created)
        """
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.tcds = tcds
        self.process_execution = process_execution


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
            validation: ValidationAssertions = all_validations_passes(),
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


def prim_asrt__any(environment: AssertionResolvingEnvironment) -> ValueAssertion:
    return asrt.anything_goes()


def prim_asrt__constant(primitive: ValueAssertion[PRIMITIVE]
                        ) -> Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]]:
    def ret_val(environment: AssertionResolvingEnvironment) -> ValueAssertion[PRIMITIVE]:
        return primitive

    return ret_val


class PrimAndExeExpectation(Generic[PRIMITIVE, OUTPUT]):
    def __init__(
            self,
            execution: ExecutionExpectation[OUTPUT] = ExecutionExpectation(),
            primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]] = prim_asrt__any,
    ):
        self.execution = execution
        self.primitive = primitive

    @staticmethod
    def of_exe(
            validation: ValidationAssertions = all_validations_passes(),
            main_result: ValueAssertion[OUTPUT] = asrt.anything_goes(),
            is_hard_error: Optional[ValueAssertion[TextRenderer]] = None,
    ) -> 'PrimAndExeExpectation[PRIMITIVE, OUTPUT]':
        return PrimAndExeExpectation(
            ExecutionExpectation(
                validation=validation,
                main_result=main_result,
                is_hard_error=is_hard_error,
            ),
            prim_asrt__any
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
    ):
        """
        :param primitive: Expectation of custom properties of the primitive object,
        i.e. properties other than the standard execution properties.
        """
        self.parse = parse
        self.execution = execution
        self.primitive = primitive

    @property
    def prim_and_exe(self) -> PrimAndExeExpectation[PRIMITIVE, OUTPUT]:
        return PrimAndExeExpectation(
            self.execution,
            self.primitive
        )


class MultiSourceExpectation(Generic[PRIMITIVE, OUTPUT]):
    def __init__(
            self,
            symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
            execution: ExecutionExpectation[OUTPUT] = ExecutionExpectation(),
            primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]] = prim_asrt__any,
    ):
        self.symbol_references = symbol_references
        self.execution = execution
        self.primitive = primitive

    @property
    def prim_and_exe(self) -> PrimAndExeExpectation[PRIMITIVE, OUTPUT]:
        return PrimAndExeExpectation(
            self.execution,
            self.primitive
        )
