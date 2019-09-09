import unittest

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.symbol.data.restrictions.value_restrictions import StringRestriction
from exactly_lib.test_case import os_services
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.test_case_utils import svh_exception
from exactly_lib.test_case_utils.condition import comparators, instruction as sut
from exactly_lib.test_case_utils.condition.comparison_structures import ComparisonHandler, OperandResolver
from exactly_lib.test_case_utils.err_msg.property_description import \
    property_descriptor_with_just_a_constant_name
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, \
    symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh, svh_assertions as asrt_svh
from exactly_lib_test.test_case.test_resources import instruction_environment
from exactly_lib_test.test_case_utils.condition.test_resources.operand_resolver import operand_resolver_that
from exactly_lib_test.test_resources import actions
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestValidation),
        unittest.makeSuite(TestMain),
    ])


THE_PROPERTY_DESCRIPTOR = property_descriptor_with_just_a_constant_name('name of property')


class TestSymbolReferences(unittest.TestCase):
    def test_symbols_from_both_operands_SHOULD_be_reported(self):
        # ARRANGE #

        symbol_reffed_by_l_op = data_symbol_utils.symbol_reference('l-op symbol')

        symbol_1_reffed_by_r_op = data_symbol_utils.symbol_reference('r-op 1 symbol')
        symbol_2_reffed_by_r_op = data_symbol_utils.symbol_reference('r-op 2 symbol',
                                                                     StringRestriction())

        l_op = operand_resolver_that(symbol_usages=[symbol_reffed_by_l_op])
        r_op = operand_resolver_that(symbol_usages=[symbol_1_reffed_by_r_op,
                                                    symbol_2_reffed_by_r_op])

        instruction = sut.Instruction(
            ComparisonHandler(THE_PROPERTY_DESCRIPTOR,
                              ExpectationType.POSITIVE,
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
                asrt_svh.is_validation_error(
                    asrt_text_doc.is_single_pre_formatted_text_that_equals('error in left op')
                ),

                operand_resolver_that(
                    validate_pre_sds=actions.do_raise(
                        svh_exception.SvhValidationException(
                            text_docs.single_pre_formatted_line_object('error in left op')
                        ))),
                operand_resolver_that(),
            ),
            (
                'validation exception in right operand',
                asrt_svh.is_validation_error(
                    asrt_text_doc.is_single_pre_formatted_text_that_equals('error in right op')
                ),

                operand_resolver_that(),
                operand_resolver_that(
                    validate_pre_sds=actions.do_raise(
                        svh_exception.SvhValidationException(
                            text_docs.single_pre_formatted_line_object('error in right op')
                        ))),
            ),
            (
                'hard error exception in left operand',
                asrt_svh.is_hard_error(
                    asrt_text_doc.is_single_pre_formatted_text_that_equals('error in left op')
                ),

                operand_resolver_that(
                    validate_pre_sds=actions.do_raise(
                        svh_exception.SvhHardErrorException(
                            text_docs.single_pre_formatted_line_object('error in left op')
                        ))),
                operand_resolver_that(),
            ),
            (
                'hard error exception in right operand',
                asrt_svh.is_hard_error(
                    asrt_text_doc.is_single_pre_formatted_text_that_equals('error in right op')
                ),

                operand_resolver_that(),
                operand_resolver_that(
                    validate_pre_sds=actions.do_raise(
                        svh_exception.SvhHardErrorException(
                            text_docs.single_pre_formatted_line_object('error in right op')
                        ))),
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
                asrt_pfh.is_hard_error(
                    asrt_text_doc.is_single_pre_formatted_text(asrt.equals('error error in left op'))
                ),

                operand_resolver_that(
                    resolve_return_value_action=actions.do_raise(
                        pfh_exception.PfhHardErrorException(
                            text_docs.single_pre_formatted_line_object('error error in left op')
                        )
                    )),
                operand_resolver_that(),
            ),
            (
                'hard error exception in right operand',
                asrt_pfh.is_hard_error(
                    asrt_text_doc.is_single_pre_formatted_text(asrt.equals('error error in right op'))
                ),

                operand_resolver_that(),
                operand_resolver_that(
                    resolve_return_value_action=actions.do_raise(
                        pfh_exception.PfhHardErrorException(
                            text_docs.single_pre_formatted_line_object('error error in right op'))
                    )
                ),
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
                asrt_pfh.is_fail__with_arbitrary_message(),
                ExpectationType.POSITIVE,
                1,
                comparators.LT,
                1,
            ),
            (
                'expectation type is negative: fail WHEN comparison succeeds',
                asrt_pfh.is_fail__with_arbitrary_message(),
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
                ComparisonHandler(THE_PROPERTY_DESCRIPTOR,
                                  expectation_type,
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


def cmp_setup(l_op: OperandResolver,
              r_op: OperandResolver) -> ComparisonHandler:
    return ComparisonHandler(THE_PROPERTY_DESCRIPTOR,
                             ExpectationType.POSITIVE,
                             l_op,
                             comparators.EQ,
                             r_op)
