import unittest
from typing import List

from exactly_lib.impls.instructions.assert_.process_output import exit_code as sut
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.condition.comparators import EQ, NE, LT, LTE, GT, GTE
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.expectations import IS_PASS, \
    IS_FAIL
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.instruction_check import \
    CHECKER, \
    PARSE_CHECKER
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.int_matchers import of_op, \
    of_neg_op
from exactly_lib_test.impls.instructions.assert_.test_resources import expression
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation2, \
    ExecutionExpectation, MultiSourceExpectation
from exactly_lib_test.impls.instructions.test_resources.instr_arr_exp import ParseExpectation
from exactly_lib_test.impls.types.integer_matcher.test_resources.abstract_syntaxes import IntegerMatcherInfixOpAbsStx, \
    IntegerMatcherComparisonAbsStx
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducerFromActResult
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.abstract_syntax import IntegerMatcherAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringSymbolAbsStx, \
    StringConcatAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.integer_matcher import \
    IntegerMatcherSymbolContextOfPrimitiveConstant


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),

        unittest.makeSuite(TestFailingValidationPreSds),
        unittest.makeSuite(TestConstantArguments),
        unittest.makeSuite(TestArgumentWithSymbolReferences),

        suite_for_instruction_documentation(
            sut.setup('instruction name').documentation),
    ])


class TheInstructionArgumentsVariantConstructor(expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparison condition string.
    """

    def apply(self,
              condition_str: str,
              ) -> str:
        return condition_str


class TheInstructionArgumentsVariantConstructorAbsStx(expression.InstructionArgumentsVariantConstructorAbsStx):
    """
    Constructs the instruction argument for a given comparison condition string.
    """

    def apply(self,
              condition: IntegerMatcherAbsStx,
              ) -> AbstractSyntax:
        return condition


class TestParse(unittest.TestCase):
    def test_invalid_syntax(self):
        test_cases = [
            ' <> 1',
            '',
            'a b c',
        ]
        for instruction_argument in test_cases:
            with self.subTest(msg=instruction_argument):
                for source in equivalent_source_variants(self, instruction_argument):
                    PARSE_CHECKER.check_invalid_arguments(self, source)

    def test_matcher_should_be_parsed_as_full_expr(self):
        lhs = IntegerMatcherSymbolContextOfPrimitiveConstant(
            'lhs',
            False,
        )
        rhs = IntegerMatcherSymbolContextOfPrimitiveConstant(
            'rhs',
            True,
        )
        symbols = [lhs, rhs]

        disjunction_syntax = IntegerMatcherInfixOpAbsStx.disjunction([lhs.abstract_syntax,
                                                                      rhs.abstract_syntax])

        CHECKER.check__abs_stx(
            self,
            disjunction_syntax,
            ArrangementPostAct2(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
                tcds=TcdsArrangementPostAct(
                    act_result=act_result_of(0)
                ),
            ),
            Expectation2(
                ParseExpectation(
                    source=asrt_source.source_is_at_end,
                    symbol_usages=SymbolContext.usages_assertion_of_contexts(symbols),
                ),
                ExecutionExpectation(
                    main_result=pfh_assertions.is_pass(),
                ),
            ),
        )


class TestFailingValidationPreSds(expression.TestFailingValidationPreSdsAbsStxBase):
    def _conf(self) -> expression.ConfigurationAbsStx:
        return expression.ConfigurationAbsStx(
            sut.Parser(),
            TheInstructionArgumentsVariantConstructorAbsStx(),
            invalid_integers_according_to_custom_validation=[-1, 256])


class TestArgumentWithSymbolReferences(unittest.TestCase):
    def test_matcher_reference(self):
        matcher_symbol = IntegerMatcherSymbolContextOfPrimitiveConstant(
            'SYMBOL',
            True,
        )
        CHECKER.check__abs_stx(
            self,
            matcher_symbol.abstract_syntax,
            ArrangementPostAct2(
                symbols=matcher_symbol.symbol_table,
                tcds=TcdsArrangementPostAct(
                    act_result=act_result_of(0),
                )
            ),
            Expectation2(
                ParseExpectation(
                    source=asrt_source.source_is_at_end,
                    symbol_usages=matcher_symbol.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=pfh_assertions.is_pass(),
                )
            ),
        )

    def test_with_symbol_references(self):
        symbol_1_name = 'symbol_1_name'
        symbol_2_name = 'symbol_2_name'

        test_cases = [
            CaseWithSymbols(
                'two argument form with a symbol that is a single integer',
                argument=IntegerMatcherComparisonAbsStx.of_cmp_op(
                    comparators.EQ,
                    StringSymbolAbsStx(symbol_1_name),
                ),
                symbol_name_and_value_list=[NameAndValue(symbol_1_name, '72')],
                actual_value_for_pass=72,
                actual_value_for_fail=87,
            ),
            CaseWithSymbols(
                'two argument form with two symbols that makes up the expected value when concatenated',
                argument=IntegerMatcherComparisonAbsStx.of_cmp_op(
                    comparators.EQ,
                    StringConcatAbsStx([
                        StringSymbolAbsStx(symbol_1_name),
                        StringSymbolAbsStx(symbol_2_name),
                    ]),
                ),
                symbol_name_and_value_list=[NameAndValue(symbol_1_name, '7'),
                                            NameAndValue(symbol_2_name, '2')],
                actual_value_for_pass=72,
                actual_value_for_fail=87,
            ),
        ]

        for case in test_cases:
            pass_fail_cases = [
                NArrEx(
                    'pass',
                    case.actual_value_for_pass,
                    pfh_assertions.is_pass(),
                ),
                NArrEx(
                    'fail',
                    case.actual_value_for_fail,
                    pfh_assertions.is_fail__with_arbitrary_message(),
                ),
            ]
            for pass_fail_case in pass_fail_cases:
                with self.subTest(name=case.name, sub_name=pass_fail_case.name):
                    CHECKER.check__abs_stx__source_variants(
                        self,
                        case.argument,
                        ArrangementPostAct2(
                            symbols=case.symbol_table,
                            tcds=TcdsArrangementPostAct(
                                act_result=act_result_of(pass_fail_case.arrangement),
                            ),
                        ),
                        MultiSourceExpectation(
                            symbol_usages=asrt.matches_sequence(
                                case.reference_assertions__string_made_up_of_just_strings),
                            execution=ExecutionExpectation(
                                main_result=pass_fail_case.expectation,
                            )
                        ),
                    )


class TestConstantArguments(unittest.TestCase):
    def test_two_argument_form(self):
        test_cases = [
            (_actual_exitcode(0), of_op(EQ, 72), IS_FAIL),
            (_actual_exitcode(72), of_op(EQ, 72), IS_PASS),

            (_actual_exitcode(72), of_neg_op(EQ, 72), IS_FAIL),
            (_actual_exitcode(72), of_neg_op(EQ, 73), IS_PASS),

            (_actual_exitcode(72), of_op(NE, 72), IS_FAIL),
            (_actual_exitcode(72), of_op(NE, 73), IS_PASS),

            (_actual_exitcode(72), of_op(LT, 28), IS_FAIL),
            (_actual_exitcode(72), of_op(LT, 72), IS_FAIL),
            (_actual_exitcode(72), of_op(LT, 87), IS_PASS),

            (_actual_exitcode(72), of_op(LTE, 28), IS_FAIL),
            (_actual_exitcode(72), of_op(LTE, 72), IS_PASS),
            (_actual_exitcode(72), of_op(LTE, 87), IS_PASS),

            (_actual_exitcode(72), of_op(GT, 28), IS_PASS),
            (_actual_exitcode(72), of_op(GT, 72), IS_FAIL),
            (_actual_exitcode(72), of_op(GT, 87), IS_FAIL),

            (_actual_exitcode(72), of_op(GTE, 28), IS_PASS),
            (_actual_exitcode(72), of_op(GTE, 72), IS_PASS),
            (_actual_exitcode(72), of_op(GTE, 87), IS_FAIL),
        ]
        for arrangement, syntax, expectation in test_cases:
            with self.subTest(syntax.as_str__default()):
                CHECKER.check__abs_stx__source_variants(
                    self,
                    syntax,
                    arrangement,
                    expectation,
                )


class CaseWithSymbols:
    def __init__(self,
                 case_name: str,
                 symbol_name_and_value_list: List[NameAndValue],
                 argument: IntegerMatcherAbsStx,
                 actual_value_for_pass: int,
                 actual_value_for_fail: int,
                 ):
        self.name = case_name
        self.argument = argument
        self.actual_value_for_pass = actual_value_for_pass
        self.actual_value_for_fail = actual_value_for_fail
        self.symbol_name_and_value_list = symbol_name_and_value_list
        self.symbol_contexts = [
            StringConstantSymbolContext(nav.name, nav.value)
            for nav in symbol_name_and_value_list
        ]

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self.symbol_contexts)

    @property
    def reference_assertions__string_made_up_of_just_strings(self) -> List[Assertion[SymbolReference]]:
        return [
            symbol_context.reference_assertion__string_made_up_of_just_strings
            for symbol_context in self.symbol_contexts
        ]


def _actual_exitcode(exit_code: int) -> ArrangementPostAct2:
    return ArrangementPostAct2(
        tcds=TcdsArrangementPostAct(
            act_result=act_result_of(exit_code)
        )
    )


def act_result_of(exit_code: int):
    return ActResultProducerFromActResult(SubProcessResult(exitcode=exit_code))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
