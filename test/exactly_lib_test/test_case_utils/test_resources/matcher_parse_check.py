import unittest
from typing import TypeVar, Generic, List, Sequence

from exactly_lib.definitions import expression
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.sdv_structure import SymbolDependentValue, SymbolContainer
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_parser \
    import remaining_source
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_file_structure.test_resources.application_environment import application_environment
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.expression.test_resources import \
    NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result

MODEL = TypeVar('MODEL')


class Configuration(Generic[MODEL]):
    def parse(self, parser: TokenParser) -> MatcherTypeSdv[MODEL]:
        raise NotImplementedError('abstract method')

    def is_reference_to(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        raise NotImplementedError('abstract method')

    def sdv_of_constant_matcher(self, matcher: MatcherWTrace[MODEL]) -> MatcherTypeSdv[MODEL]:
        raise NotImplementedError('abstract method')

    def sdv_of_constant_result_matcher(self, result: bool) -> MatcherTypeSdv[MODEL]:
        return self.sdv_of_constant_matcher(self.constant_matcher(result))

    def container_with_sdv_of_constant_matcher(self, matcher: MatcherWTrace[MODEL]) -> SymbolContainer:
        return container(self.sdv_of_constant_matcher(matcher))

    def arbitrary_model_that_should_not_be_touched(self) -> MODEL:
        raise NotImplementedError('abstract method')

    def constant_matcher(self, result: bool) -> MatcherWTrace[MODEL]:
        raise NotImplementedError('abstract method')


class ExecutionExpectation:
    def __init__(self,
                 result: bool,
                 operands: List[bool]):
        self.result = result
        self.operands = operands

    @property
    def name(self) -> str:
        return 'result={}, operands={}'.format(self.result,
                                               self.operands)


class Expectation:
    def __init__(self,
                 sdv: ValueAssertion[SymbolDependentValue],
                 token_stream: ValueAssertion[TokenParser] = asrt.anything_goes()):
        self.sdv = sdv
        self.token_stream = token_stream


class TestParseStandardExpressionsBase(unittest.TestCase):
    TCDS = fake_tcds()
    APPLICATION_ENVIRONMENT = application_environment()

    @property
    def conf(self) -> Configuration:
        raise NotImplementedError('abstract method')

    def _check(self,
               source: TokenParser,
               expectation: Expectation):
        # ACT #
        actual_sdv = self.conf.parse(source)
        # ASSERT #
        expectation.sdv.apply_with_message(self,
                                           actual_sdv,
                                           'SDV')
        expectation.token_stream.apply_with_message(self,
                                                    source.token_stream,
                                                    'token stream')

    def _check_execution(self,
                         source: str,
                         references: List[str],
                         expectations: Sequence[ExecutionExpectation]):
        conf = self.conf
        # ACT #
        actual_sdv = conf.parse(remaining_source(source))
        # ASSERT #
        references_expectation = asrt.matches_sequence([
            conf.is_reference_to(reference)
            for reference in references
        ])
        references_expectation.apply_with_message(
            self,
            actual_sdv.references,
            'references',
        )
        model = conf.arbitrary_model_that_should_not_be_touched()

        for expectation in expectations:
            with self.subTest(expectation.name):
                self.assertEqual(len(references),
                                 len(expectation.operands),
                                 'test case setup: number of operands must equal number of references')
                symbols = symbol_utils.symbol_table_from_name_and_sdvs(
                    [
                        NameAndValue(sym_name,
                                     conf.sdv_of_constant_result_matcher(result)
                                     )
                        for sym_name, result in zip(references, expectation.operands)
                    ]
                )
                ddv = actual_sdv.resolve(symbols)
                adv = ddv.value_of_any_dependency(self.TCDS)
                matcher = adv.applier(self.APPLICATION_ENVIRONMENT)
                self.assertIsInstance(matcher, MatcherWTrace,
                                      'primitive value should be instance of ' + str(type(MatcherWTrace)))
                assert isinstance(matcher, MatcherWTrace)

                actual_result = matcher.matches_w_trace(model)
                asrt_matching_result.matches_value(expectation.result).apply_with_message(self,
                                                                                          actual_result,
                                                                                          'matching result')

    def test_failing_parse(self):
        cases = [
            (
                'neither a symbol, nor a matcher',
                remaining_source(NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    self.conf.parse(source)

    def test_reference(self):
        # ARRANGE #
        symbol_name = 'the_symbol_name'

        # ACT & ASSERT #
        self._check_execution(
            symbol_name,
            references=[symbol_name],
            expectations=[
                ExecutionExpectation(False, [False]),
                ExecutionExpectation(True, [True]),
            ],
        )

    def test_not(self):
        # ARRANGE #
        symbol_name = 'the_symbol_name'

        # ACT & ASSERT #
        self._check_execution(
            '{not_} {symbol}'.format(not_=expression.NOT_OPERATOR_NAME,
                                     symbol=symbol_name),
            references=[symbol_name],
            expectations=[
                ExecutionExpectation(True, [False]),
                ExecutionExpectation(False, [True]),
            ],
        )

    def test_and(self):
        # ARRANGE #
        symbol_1 = 'the_symbol_1_name'
        symbol_2 = 'the_symbol_2_name'
        # ACT & ASSERT #
        self._check_execution(
            '{symbol_1} {and_op} {symbol_2}'.format(
                symbol_1=symbol_1,
                and_op=expression.AND_OPERATOR_NAME,
                symbol_2=symbol_2,
            ),
            references=[symbol_1, symbol_2],
            expectations=[
                ExecutionExpectation(False, [False, False]),
                ExecutionExpectation(False, [False, True]),
                ExecutionExpectation(False, [True, False]),
                ExecutionExpectation(True, [True, True]),
            ])

    def test_or(self):
        # ARRANGE #
        symbol_1 = 'the_symbol_1_name'
        symbol_2 = 'the_symbol_2_name'
        # ACT & ASSERT #
        self._check_execution(
            '{symbol_1} {and_op} {symbol_2}'.format(
                symbol_1=symbol_1,
                and_op=expression.OR_OPERATOR_NAME,
                symbol_2=symbol_2,
            ),
            references=[symbol_1, symbol_2],
            expectations=[
                ExecutionExpectation(False, [False, False]),
                ExecutionExpectation(True, [False, True]),
                ExecutionExpectation(True, [True, False]),
                ExecutionExpectation(True, [True, True]),
            ])
