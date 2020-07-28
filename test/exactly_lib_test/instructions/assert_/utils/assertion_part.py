import unittest
from typing import Sequence

from exactly_lib.instructions.assert_.utils import assertion_part as sut
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.sdv_validation import ConstantSuccessSdvValidator
from exactly_lib.test_case import os_services_access as oss
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.common.test_resources.text_doc_assertions import is_string_for_test
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh, svh_assertions as asrt_svh
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_validator import SdvValidatorThat
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAssertionPart),
        unittest.makeSuite(TestSequence),
        unittest.makeSuite(TestAssertionInstructionFromAssertionPart),
    ])


class TestAssertionPart(unittest.TestCase):
    the_os_services = oss.new_for_current_os()
    environment = fake_post_sds_environment()

    def test_return_pfh_pass_WHEN_no_exception_is_raised(self):
        # ARRANGE #
        assertion_part_that_not_raises = SuccessfulPartThatReturnsConstructorArgPlusOne()
        # ACT #
        actual = assertion_part_that_not_raises.check_and_return_pfh(self.environment,
                                                                     self.the_os_services,
                                                                     1)
        # ASSERT #
        assertion = asrt_pfh.is_pass()
        assertion.apply_without_message(self, actual)

    def test_return_pfh_fail_WHEN_PfhFailException_is_raised(self):
        # ARRANGE #
        assertion_part_that_raises = PartThatRaisesFailureExceptionIfArgumentIsEqualToOne()
        # ACT #
        actual = assertion_part_that_raises.check_and_return_pfh(self.environment,
                                                                 self.the_os_services,
                                                                 1)
        # ASSERT #
        assertion = asrt_pfh.is_fail(
            is_string_for_test(
                asrt.equals(PartThatRaisesFailureExceptionIfArgumentIsEqualToOne.ERROR_MESSAGE))
        )
        assertion.apply_without_message(self, actual)


class TestSequence(unittest.TestCase):
    the_os_services = oss.new_for_current_os()
    environment = fake_post_sds_environment()

    def test_WHEN_list_of_assertion_parts_is_empty_THEN_no_exception_SHOULD_be_raised(self):
        # ARRANGE #
        assertion_part = sut.SequenceOfCooperativeAssertionParts([])
        # ACT & ASSERT #
        assertion_part.check(self.environment, self.the_os_services, 'arg that is not used')

    def test_WHEN_single_successful_assertion_part_THEN_that_assertion_part_should_have_been_executed(self):
        # ARRANGE #
        assertion_part = sut.SequenceOfCooperativeAssertionParts([SuccessfulPartThatReturnsConstructorArgPlusOne()])
        # ACT #
        actual = assertion_part.check(self.environment, self.the_os_services, 0)
        # ASSERT #
        self.assertEqual(1,
                         actual,
                         'one assertion_part should have been executed')

    def test_WHEN_multiple_successful_assertion_parts_THEN_that_all_assertion_parts_should_have_been_executed(self):
        # ARRANGE #
        assertion_part = sut.SequenceOfCooperativeAssertionParts([SuccessfulPartThatReturnsConstructorArgPlusOne(),
                                                                  SuccessfulPartThatReturnsConstructorArgPlusOne()])
        # ACT #
        actual = assertion_part.check(self.environment, self.the_os_services, 0)
        # ASSERT #
        self.assertEqual(2,
                         actual,
                         'two assertion_part should have been executed')

    def test_WHEN_a_failing_assertion_part_SHOULD_stop_execution_and_report_the_failure(self):
        # ARRANGE #
        assertion_part = sut.SequenceOfCooperativeAssertionParts([
            SuccessfulPartThatReturnsConstructorArgPlusOne(),
            PartThatRaisesFailureExceptionIfArgumentIsEqualToOne(),
            SuccessfulPartThatReturnsConstructorArgPlusOne(),
        ])
        # ACT & ASSERT #
        with self.assertRaises(pfh_exception.PfhFailException) as cm:
            assertion_part.check(self.environment, self.the_os_services, 0)
        assertion = asrt_text_doc.is_single_pre_formatted_text_that_equals(
            PartThatRaisesFailureExceptionIfArgumentIsEqualToOne.ERROR_MESSAGE
        )
        assertion.apply_with_message(
            self,
            cm.exception.err_msg,
            'error message from failing assertion_part should appear in PFH exception'
        )

    def test_references_from_assertion_part_SHOULD_be_reported(self):
        # ARRANGE #
        ref_1_info = NameAndValue('ref 1', ValueType.FILE_MATCHER)

        ref_1 = SymbolReference(ref_1_info.name,
                                ValueTypeRestriction(ref_1_info.value))

        expected_references = asrt.matches_sequence([
            asrt_sym_usage.matches_reference(asrt.equals(ref_1_info.name),
                                             is_value_type_restriction(ref_1_info.value)),
        ])

        assertion_part_with_references = PartWithReference([ref_1])
        instruction = sut.AssertionInstructionFromAssertionPart(assertion_part_with_references,
                                                                lambda env: 'not used in this test')

        # ACT #
        actual = instruction.symbol_usages()
        # ASSERT #
        expected_references.apply_without_message(self, actual)

    def test_WHEN_validation_of_every_assertion_part_is_successful_THEN_validation_SHOULD_succeed(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'empty list of assertion_parts',
                sut.SequenceOfCooperativeAssertionParts([])
            ),
            NameAndValue(
                'validation of every assertion_part is successful',
                sut.SequenceOfCooperativeAssertionParts([PartForValidation(SdvValidatorThat()),
                                                         PartForValidation(SdvValidatorThat())])
            ),
        ]
        validation_environment = self.environment.path_resolving_environment_pre_or_post_sds
        for case in cases:
            with self.subTest(case=case.name):
                sequence_part = case.value
                with self.subTest(name='pre sds validation'):
                    # ACT #
                    actual = sequence_part.validator.validate_pre_sds_if_applicable(validation_environment)
                    # ASSERT #
                    self.assertIsNone(actual)

                with self.subTest(name='post setup validation'):
                    # ACT #
                    actual = sequence_part.validator.validate_post_sds_if_applicable(validation_environment)
                    # ASSERT #
                    self.assertIsNone(actual)

    def test_WHEN_a_validator_fails_pre_sds_THEN_validation_SHOULD_fail_pre_sds(self):
        # ARRANGE #
        the_error_message = 'the error message'
        assertion_part_with_successful_validation = PartForValidation(SdvValidatorThat())
        assertion_part_with_unsuccessful_validation = PartForValidation(SdvValidatorThat(
            pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test(the_error_message))
        )
        sequence_checker = sut.SequenceOfCooperativeAssertionParts([assertion_part_with_successful_validation,
                                                                    assertion_part_with_unsuccessful_validation])
        validation_environment = self.environment.path_resolving_environment_pre_or_post_sds
        # ACT #
        actual = sequence_checker.validator.validate_pre_sds_if_applicable(validation_environment)
        # ASSERT #
        asrt_text_doc.is_string_for_test_that_equals(the_error_message).apply_without_message(
            self,
            actual,
        )

    def test_WHEN_a_validator_fails_post_setup_THEN_validation_SHOULD_fail_post_setup(self):
        # ARRANGE #
        the_error_message = 'the error message'
        assertion_part_with_successful_validation = PartForValidation(SdvValidatorThat())
        assertion_part_with_unsuccessful_validation = PartForValidation(SdvValidatorThat(
            post_setup_return_value=asrt_text_doc.new_single_string_text_for_test(the_error_message))
        )
        sequence_checker = sut.SequenceOfCooperativeAssertionParts([assertion_part_with_successful_validation,
                                                                    assertion_part_with_unsuccessful_validation])
        validation_environment = self.environment.path_resolving_environment_pre_or_post_sds
        # ACT #
        pre_sds_result = sequence_checker.validator.validate_pre_sds_if_applicable(validation_environment)
        post_sds_result = sequence_checker.validator.validate_post_sds_if_applicable(validation_environment)
        # ASSERT #
        self.assertIsNone(pre_sds_result,
                          'pre sds validation should succeed')
        asrt_text_doc.is_string_for_test_that_equals(the_error_message).apply_with_message(
            self,
            post_sds_result,
            'post setup validation should fail',
        )


class TestAssertionInstructionFromAssertionPart(unittest.TestCase):
    the_os_services = oss.new_for_current_os()

    def test_argument_getter_SHOULD_be_given_environment_as_argument(self):
        # ARRANGE #
        environment = fake_post_sds_environment()

        assertion_part = PartThatRaisesFailureExceptionIfArgumentIsEqualToOne()

        def argument_getter_that_depends_on_environment(env: InstructionEnvironmentForPostSdsStep) -> int:
            return 1 if env is environment else 0

        instruction = sut.AssertionInstructionFromAssertionPart(assertion_part,
                                                                argument_getter_that_depends_on_environment)
        # ACT #
        actual = instruction.main(environment, self.the_os_services)
        # ASSERT #
        assertion = asrt_pfh.is_fail(
            asrt_text_doc.is_string_for_test(
                asrt.equals(PartThatRaisesFailureExceptionIfArgumentIsEqualToOne.ERROR_MESSAGE)
            )
        )
        assertion.apply_without_message(self, actual)

    def test_return_pfh_pass_WHEN_no_exception_is_raised(self):
        # ARRANGE #
        environment = fake_post_sds_environment()

        assertion_part_that_not_raises = SuccessfulPartThatReturnsConstructorArgPlusOne()
        instruction = sut.AssertionInstructionFromAssertionPart(assertion_part_that_not_raises,
                                                                lambda env: 0)
        # ACT #
        actual = instruction.main(environment, self.the_os_services)
        # ASSERT #
        assertion = asrt_pfh.is_pass()
        assertion.apply_without_message(self, actual)

    def test_return_pfh_fail_WHEN_PfhFailException_is_raised(self):
        # ARRANGE #
        environment = fake_post_sds_environment()

        assertion_part_that_raises = PartThatRaisesFailureExceptionIfArgumentIsEqualToOne()
        instruction = sut.AssertionInstructionFromAssertionPart(assertion_part_that_raises,
                                                                lambda env: 1)
        # ACT #
        actual = instruction.main(environment, self.the_os_services)
        # ASSERT #
        assertion = asrt_pfh.is_fail(
            asrt_text_doc.is_string_for_test(
                asrt.equals(PartThatRaisesFailureExceptionIfArgumentIsEqualToOne.ERROR_MESSAGE))
        )
        assertion.apply_without_message(self, actual)

    def test_WHEN_no_validator_is_given_THEN_validation_SHOULD_succeed(self):
        # ARRANGE #
        environment = fake_post_sds_environment()

        assertion_part_without_validation = PartForValidation()
        instruction = sut.AssertionInstructionFromAssertionPart(assertion_part_without_validation,
                                                                lambda env: 'argument to assertion_part')
        with self.subTest(name='pre sds validation'):
            # ACT #
            actual = instruction.validate_pre_sds(environment)
            # ASSERT #
            asrt_svh.is_success().apply_without_message(self, actual)

        with self.subTest(name='post setup validation'):
            # ACT #
            actual = instruction.validate_post_setup(environment)
            # ASSERT #
            asrt_svh.is_success().apply_without_message(self, actual)

    def test_WHEN_a_successful_validator_is_given_THEN_validation_SHOULD_succeed(self):
        # ARRANGE #
        environment = fake_post_sds_environment()

        assertion_part_without_validation = PartForValidation(ConstantSuccessSdvValidator())
        instruction = sut.AssertionInstructionFromAssertionPart(assertion_part_without_validation,
                                                                lambda env: 'argument to assertion_part')
        with self.subTest(name='pre sds validation'):
            # ACT #
            actual = instruction.validate_pre_sds(environment)
            # ASSERT #
            asrt_svh.is_success().apply_without_message(self, actual)

        with self.subTest(name='post setup validation'):
            # ACT #
            actual = instruction.validate_post_setup(environment)
            # ASSERT #
            asrt_svh.is_success().apply_without_message(self, actual)

    def test_WHEN_given_validator_fails_pre_sds_THEN_validation_SHOULD_fail_pre_sds(self):
        # ARRANGE #
        environment = fake_post_sds_environment()

        the_error_message = 'the error message'
        assertion_part = PartForValidation(SdvValidatorThat(
            pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test(the_error_message))
        )
        instruction = sut.AssertionInstructionFromAssertionPart(assertion_part,
                                                                lambda env: 'argument to assertion_part')
        # ACT #
        actual = instruction.validate_pre_sds(environment)
        # ASSERT #
        assertion = asrt_svh.is_validation_error(
            asrt_text_doc.is_single_pre_formatted_text_that_equals(the_error_message)
        )
        assertion.apply_without_message(self, actual)

    def test_WHEN_given_validator_fails_post_setup_THEN_main_SHOULD_report_hard_error(self):
        # ARRANGE #
        environment = fake_post_sds_environment()

        the_error_message = 'the error message'
        assertion_part = PartForValidation(SdvValidatorThat(
            post_setup_return_value=asrt_text_doc.new_single_string_text_for_test(the_error_message))
        )
        instruction = sut.AssertionInstructionFromAssertionPart(assertion_part,
                                                                lambda env: 'argument to assertion_part')
        is_validation_success = asrt_svh.is_success()
        main_result_is_hard_error = asrt_pfh.is_hard_error(
            asrt_text_doc.is_single_pre_formatted_text_that_equals(the_error_message)
        )

        # ACT & ASSERT #

        pre_sds_result = instruction.validate_pre_sds(environment)
        is_validation_success.apply_with_message(self, pre_sds_result,
                                                 'pre sds validation should succeed')
        post_sds_result = instruction.validate_post_setup(environment)
        is_validation_success.apply_with_message(self, post_sds_result,
                                                 'post setup validation should succeed')
        main_result = instruction.main(environment, self.the_os_services)

        main_result_is_hard_error.apply_with_message(self,
                                                     main_result,
                                                     'main should fail')


class PartForValidation(sut.AssertionPart[int, int]):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        raise NotImplementedError('this method should not be used')


class SuccessfulPartThatReturnsConstructorArgPlusOne(sut.AssertionPart[int, int]):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        return arg + 1


class PartThatRaisesFailureExceptionIfArgumentIsEqualToOne(sut.AssertionPart[int, int]):
    ERROR_MESSAGE = 'error message of FAILING assertion_part'

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        if arg == 1:
            raise pfh_exception.PfhFailException(asrt_text_doc.new_single_string_text_for_test(self.ERROR_MESSAGE))
        else:
            return arg + 1


class PartWithReference(sut.AssertionPart[int, None]):
    def __init__(self, references: Sequence[SymbolReference]):
        super().__init__()
        self._references = references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        pass
