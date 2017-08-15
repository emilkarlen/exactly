import unittest

from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.instructions.assert_.utils.expression import instruction as sut
from exactly_lib.instructions.assert_.utils.expression.comparison_structures import ComparisonHandler, OperandResolver
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhHardErrorException
from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.instructions.utils.return_svh_via_exceptions import SvhValidationException, SvhHardErrorException
from exactly_lib.symbol.restrictions.value_restrictions import StringRestriction
from exactly_lib.test_case import os_services
from exactly_lib_test.instructions.assert_.utils.expression.test_resources.operand_resolver import operand_resolver_that
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case.test_resources import instruction_environment
from exactly_lib_test.test_case_utils.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_resources import actions
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestValidation),
        unittest.makeSuite(TestMain),
    ])


class TestSymbolReferences(unittest.TestCase):
    def test_symbols_from_both_operands_SHOULD_be_reported(self):
        # ARRANGE #

        symbol_reffed_by_l_op = symbol_utils.symbol_reference('l-op symbol')

        symbol_1_reffed_by_r_op = symbol_utils.symbol_reference('r-op 1 symbol')
        symbol_2_reffed_by_r_op = symbol_utils.symbol_reference('r-op 2 symbol',
                                                                StringRestriction())

        l_op = operand_resolver_that(symbol_usages=[symbol_reffed_by_l_op])
        r_op = operand_resolver_that(symbol_usages=[symbol_1_reffed_by_r_op,
                                                    symbol_2_reffed_by_r_op])

        instruction = sut.Instruction(
            ComparisonHandler(ExpectationType.POSITIVE,
                              l_op, comparators.EQ, r_op))

        # ACT #

        actual = instruction.symbol_usages()

        # ASSERT #

        expected_references = [
            symbol_reffed_by_l_op,
            symbol_1_reffed_by_r_op,
            symbol_2_reffed_by_r_op,
        ]

        assertion = asrt_sym_ref.equals_symbol_references(expected_references)

        assertion.apply_without_message(self, actual)


class TestValidation(unittest.TestCase):
    def test_validation_pre_sds(self):
        the_instruction_environment = instruction_environment.fake_pre_sds_environment()

        cases = [
            (
                'validation should succeed when both operands succeed',
                asrt_svh.is_success(),

                operand_resolver_that(),
                operand_resolver_that(),
            ),
            (
                'validation exception in left operand',
                asrt_svh.is_validation_error(asrt.equals('error in left op')),

                operand_resolver_that(
                    validate_pre_sds=actions.do_raise(SvhValidationException('error in left op'))),
                operand_resolver_that(),
            ),
            (
                'validation exception in right operand',
                asrt_svh.is_validation_error(asrt.equals('error in right op')),

                operand_resolver_that(),
                operand_resolver_that(
                    validate_pre_sds=actions.do_raise(SvhValidationException('error in right op'))),
            ),
            (
                'hard error exception in left operand',
                asrt_svh.is_hard_error(asrt.equals('error in left op')),

                operand_resolver_that(
                    validate_pre_sds=actions.do_raise(SvhHardErrorException('error in left op'))),
                operand_resolver_that(),
            ),
            (
                'hard error exception in right operand',
                asrt_svh.is_hard_error(asrt.equals('error in right op')),

                operand_resolver_that(),
                operand_resolver_that(
                    validate_pre_sds=actions.do_raise(SvhHardErrorException('error in right op'))),
            ),
        ]

        for name, result_assertion, l_op, r_op in cases:
            instruction_to_check = sut.Instruction(cmp_setup(l_op, r_op))
            with self.subTest(name=name):
                # ACT #

                actual = instruction_to_check.validate_pre_sds(the_instruction_environment)

                # ASSERT #

                result_assertion.apply_without_message(self, actual)


class TestMain(unittest.TestCase):
    def test_hard_error(self):
        the_instruction_environment = instruction_environment.fake_post_sds_environment()
        the_os_services = os_services.new_default()

        cases = [
            (
                'hard error exception in left operand',
                asrt_pfh.is_hard_error(asrt.equals('error error in left op')),

                operand_resolver_that(
                    resolve_return_value_action=actions.do_raise(PfhHardErrorException('error error in left op'))),
                operand_resolver_that(),
            ),
            (
                'hard error exception in right operand',
                asrt_pfh.is_hard_error(asrt.equals('error error in right op')),

                operand_resolver_that(),
                operand_resolver_that(
                    resolve_return_value_action=actions.do_raise(PfhHardErrorException('error error in right op'))),
            ),
        ]

        for name, result_assertion, l_op, r_op in cases:
            instruction_to_check = sut.Instruction(cmp_setup(l_op, r_op))
            with self.subTest(name=name):
                # ACT #

                actual = instruction_to_check.main(the_instruction_environment,
                                                   the_os_services)

                # ASSERT #

                result_assertion.apply_without_message(self, actual)

    def test_evaluation_of_comparison(self):
        the_instruction_environment = instruction_environment.fake_post_sds_environment()
        the_os_services = os_services.new_default()

        cases = [
            (
                'expectation type is positive: pass WHEN comparison succeeds',
                asrt_pfh.is_pass(),
                ExpectationType.POSITIVE,
                1,
                comparators.LT,
                2,
            ),
            (
                'expectation type is positive: fail WHEN comparison does not succeeds',
                asrt_pfh.is_fail(ASSERT_ERROR_MESSAGE_IS_A_STRING),
                ExpectationType.POSITIVE,
                1,
                comparators.LT,
                1,
            ),
            (
                'expectation type is negative: fail WHEN comparison succeeds',
                asrt_pfh.is_fail(ASSERT_ERROR_MESSAGE_IS_A_STRING),
                ExpectationType.NEGATIVE,
                1,
                comparators.LT,
                2,
            ),
            (
                'expectation type is negative: pass WHEN comparison does not succeeds',
                asrt_pfh.is_pass(),
                ExpectationType.NEGATIVE,
                1,
                comparators.LT,
                1,
            ),
        ]

        for name, result_assertion, expectation_type, l_op, op, r_op in cases:
            # ARRANGE #
            instruction_to_check = sut.Instruction(
                ComparisonHandler(expectation_type,
                                  operand_resolver_that(
                                    resolve_return_value_action=do_return(l_op)),
                                  op,
                                  operand_resolver_that(
                                    resolve_return_value_action=do_return(r_op))))
            with self.subTest(name=name):
                # ACT #

                actual = instruction_to_check.main(the_instruction_environment,
                                                   the_os_services)

                # ASSERT #

                result_assertion.apply_without_message(self, actual)


ASSERT_ERROR_MESSAGE_IS_A_STRING = asrt.is_instance(str)


def cmp_setup(l_op: OperandResolver,
              r_op: OperandResolver) -> ComparisonHandler:
    return ComparisonHandler(ExpectationType.POSITIVE,
                             l_op,
                             comparators.EQ,
                             r_op)
