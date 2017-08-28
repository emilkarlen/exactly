import unittest

from exactly_lib.instructions.assert_.utils import checker as sut
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.restriction import ElementTypeRestriction
from exactly_lib.test_case import os_services as oss
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.type_system_values.value_type import ElementType
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.instructions.test_resources.pre_or_post_sds_validator import ValidatorThat
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_rs
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_element_type_restriction
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_case_utils.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestChecker),
        unittest.makeSuite(TestSequence),
        unittest.makeSuite(TestAssertionInstructionFromChecker),
    ])


class TestChecker(unittest.TestCase):
    the_os_services = oss.new_default()
    environment = fake_post_sds_environment()

    def test_return_pfh_pass_WHEN_no_exception_is_raised(self):
        # ARRANGE #
        checker_that_not_raises = SuccessfulCheckerThatReturnsConstructorArgPlusOne()
        # ACT #
        actual = checker_that_not_raises.check_and_return_pfh(self.environment,
                                                              self.the_os_services,
                                                              1)
        # ASSERT #
        assertion = asrt_pfh.is_pass()
        assertion.apply_without_message(self, actual)

    def test_return_pfh_fail_WHEN_PfhFailException_is_raised(self):
        # ARRANGE #
        checker_that_raises = CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne()
        # ACT #
        actual = checker_that_raises.check_and_return_pfh(self.environment,
                                                          self.the_os_services,
                                                          1)
        # ASSERT #
        assertion = asrt_pfh.is_fail(
            asrt.equals(CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne.ERROR_MESSAGE))
        assertion.apply_without_message(self, actual)


class TestSequence(unittest.TestCase):
    the_os_services = oss.new_default()
    environment = fake_post_sds_environment()

    def test_WHEN_list_of_checkers_is_empty_THEN_no_exception_SHOULD_be_raised(self):
        # ARRANGE #
        checker = sut.SequenceOfChecks([])
        # ACT & ASSERT #
        checker.check(self.environment, self.the_os_services, 'arg that is not used')

    def test_WHEN_single_successful_checker_THEN_that_checker_should_have_been_executed(self):
        # ARRANGE #
        checker = sut.SequenceOfChecks([SuccessfulCheckerThatReturnsConstructorArgPlusOne()])
        # ACT #
        actual = checker.check(self.environment, self.the_os_services, 0)
        # ASSERT #
        self.assertEqual(1,
                         actual,
                         'one checker should have been executed')

    def test_WHEN_multiple_successful_checkers_THEN_that_all_checkers_should_have_been_executed(self):
        # ARRANGE #
        checker = sut.SequenceOfChecks([SuccessfulCheckerThatReturnsConstructorArgPlusOne(),
                                        SuccessfulCheckerThatReturnsConstructorArgPlusOne()])
        # ACT #
        actual = checker.check(self.environment, self.the_os_services, 0)
        # ASSERT #
        self.assertEqual(2,
                         actual,
                         'two checker should have been executed')

    def test_WHEN_a_failing_checker_SHOULD_stop_execution_and_report_the_failure(self):
        # ARRANGE #
        checker = sut.SequenceOfChecks([SuccessfulCheckerThatReturnsConstructorArgPlusOne(),
                                        CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne(),
                                        SuccessfulCheckerThatReturnsConstructorArgPlusOne()])
        # ACT & ASSERT #
        with self.assertRaises(PfhFailException) as cm:
            checker.check(self.environment, self.the_os_services, 0)
        self.assertEqual(CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne.ERROR_MESSAGE,
                         cm.exception.err_msg,
                         'error message from failing checker should appear in PFH exception')

    def test_references_from_checker_SHOULD_be_reported(self):
        # ARRANGE #
        ref_1_info = NameAndValue('ref 1', ElementType.LOGIC)

        ref_1 = NamedElementReference(ref_1_info.name,
                                      ElementTypeRestriction(ref_1_info.value))

        expected_references = asrt.matches_sequence([
            asrt_rs.matches_reference(asrt.equals(ref_1_info.name),
                                      is_element_type_restriction(ref_1_info.value)),
        ])

        checker_with_references = CheckerWithReference([ref_1])
        instruction = sut.AssertionInstructionFromChecker(checker_with_references,
                                                          lambda env: 'not used in this test')

        # ACT #
        actual = instruction.symbol_usages()
        # ASSERT #
        expected_references.apply_without_message(self, actual)

    def test_WHEN_validation_of_every_checker_is_successful_THEN_validation_SHOULD_succeed(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'empty list of checkers',
                sut.SequenceOfChecks([])
            ),
            NameAndValue(
                'validation of every checker is successful',
                sut.SequenceOfChecks([CheckerForValidation(ValidatorThat()),
                                      CheckerForValidation(ValidatorThat())])
            ),
        ]
        validation_environment = self.environment.path_resolving_environment_pre_or_post_sds
        for case in cases:
            with self.subTest(case=case.name):
                sequence_checker = case.value
                with self.subTest(name='pre sds validation'):
                    # ACT #
                    actual = sequence_checker.validator.validate_pre_sds_if_applicable(validation_environment)
                    # ASSERT #
                    self.assertIsNone(actual)

                with self.subTest(name='post setup validation'):
                    # ACT #
                    actual = sequence_checker.validator.validate_post_sds_if_applicable(validation_environment)
                    # ASSERT #
                    self.assertIsNone(actual)

    def test_WHEN_a_validator_fails_pre_sds_THEN_validation_SHOULD_fail_pre_sds(self):
        # ARRANGE #
        the_error_message = 'the error message'
        checker_with_successful_validation = CheckerForValidation(ValidatorThat())
        checker_with_unsuccessful_validation = CheckerForValidation(ValidatorThat(
            pre_sds_return_value=the_error_message))
        sequence_checker = sut.SequenceOfChecks([checker_with_successful_validation,
                                                 checker_with_unsuccessful_validation])
        validation_environment = self.environment.path_resolving_environment_pre_or_post_sds
        # ACT #
        actual = sequence_checker.validator.validate_pre_sds_if_applicable(validation_environment)
        # ASSERT #
        self.assertEqual(the_error_message,
                         actual)

    def test_WHEN_a_validator_fails_post_setup_THEN_validation_SHOULD_fail_post_setup(self):
        # ARRANGE #
        the_error_message = 'the error message'
        checker_with_successful_validation = CheckerForValidation(ValidatorThat())
        checker_with_unsuccessful_validation = CheckerForValidation(ValidatorThat(
            post_setup_return_value=the_error_message))
        sequence_checker = sut.SequenceOfChecks([checker_with_successful_validation,
                                                 checker_with_unsuccessful_validation])
        validation_environment = self.environment.path_resolving_environment_pre_or_post_sds
        # ACT #
        pre_sds_result = sequence_checker.validator.validate_pre_sds_if_applicable(validation_environment)
        post_sds_result = sequence_checker.validator.validate_post_sds_if_applicable(validation_environment)
        # ASSERT #
        self.assertIsNone(pre_sds_result,
                          'pre sds validation should succeed')
        self.assertEqual(the_error_message,
                         post_sds_result,
                         'post setup validation should fail')


class TestAssertionInstructionFromChecker(unittest.TestCase):
    the_os_services = oss.new_default()
    environment = fake_post_sds_environment()

    def test_argument_getter_SHOULD_be_given_environment_as_argument(self):
        # ARRANGE #
        checker = CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne()

        def argument_getter_that_depends_on_environment(env: InstructionEnvironmentForPostSdsStep) -> int:
            return 1 if env is self.environment else 0

        instruction = sut.AssertionInstructionFromChecker(checker,
                                                          argument_getter_that_depends_on_environment)
        # ACT #
        actual = instruction.main(self.environment, self.the_os_services)
        # ASSERT #
        assertion = asrt_pfh.is_fail(asrt.equals(CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne.ERROR_MESSAGE))
        assertion.apply_without_message(self, actual)

    def test_return_pfh_pass_WHEN_no_exception_is_raised(self):
        # ARRANGE #
        checker_that_not_raises = SuccessfulCheckerThatReturnsConstructorArgPlusOne()
        instruction = sut.AssertionInstructionFromChecker(checker_that_not_raises,
                                                          lambda env: 0)
        # ACT #
        actual = instruction.main(self.environment, self.the_os_services)
        # ASSERT #
        assertion = asrt_pfh.is_pass()
        assertion.apply_without_message(self, actual)

    def test_return_pfh_fail_WHEN_PfhFailException_is_raised(self):
        # ARRANGE #
        checker_that_raises = CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne()
        instruction = sut.AssertionInstructionFromChecker(checker_that_raises,
                                                          lambda env: 1)
        # ACT #
        actual = instruction.main(self.environment, self.the_os_services)
        # ASSERT #
        assertion = asrt_pfh.is_fail(
            asrt.equals(CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne.ERROR_MESSAGE))
        assertion.apply_without_message(self, actual)

    def test_WHEN_no_validator_is_given_THEN_validation_SHOULD_succeed(self):
        # ARRANGE #
        checker_without_validation = CheckerForValidation()
        instruction = sut.AssertionInstructionFromChecker(checker_without_validation,
                                                          lambda env: 'argument to checker')
        with self.subTest(name='pre sds validation'):
            # ACT #
            actual = instruction.validate_pre_sds(self.environment)
            # ASSERT #
            asrt_svh.is_success().apply_without_message(self, actual)

        with self.subTest(name='post setup validation'):
            # ACT #
            actual = instruction.validate_post_setup(self.environment)
            # ASSERT #
            asrt_svh.is_success().apply_without_message(self, actual)

    def test_WHEN_a_successful_validator_is_given_THEN_validation_SHOULD_succeed(self):
        # ARRANGE #
        checker_without_validation = CheckerForValidation(ConstantSuccessValidator())
        instruction = sut.AssertionInstructionFromChecker(checker_without_validation,
                                                          lambda env: 'argument to checker')
        with self.subTest(name='pre sds validation'):
            # ACT #
            actual = instruction.validate_pre_sds(self.environment)
            # ASSERT #
            asrt_svh.is_success().apply_without_message(self, actual)

        with self.subTest(name='post setup validation'):
            # ACT #
            actual = instruction.validate_post_setup(self.environment)
            # ASSERT #
            asrt_svh.is_success().apply_without_message(self, actual)

    def test_WHEN_given_validator_fails_pre_sds_THEN_validation_SHOULD_fail_pre_sds(self):
        # ARRANGE #
        the_error_message = 'the error message'
        checker = CheckerForValidation(ValidatorThat(
            pre_sds_return_value=the_error_message))
        instruction = sut.AssertionInstructionFromChecker(checker,
                                                          lambda env: 'argument to checker')
        # ACT #
        actual = instruction.validate_pre_sds(self.environment)
        # ASSERT #
        assertion = asrt_svh.is_validation_error(asrt.equals(the_error_message))
        assertion.apply_without_message(self, actual)

    def test_WHEN_given_validator_fails_post_setup_THEN_validation_SHOULD_fail_post_setup(self):
        # ARRANGE #
        the_error_message = 'the error message'
        checker = CheckerForValidation(ValidatorThat(
            post_setup_return_value=the_error_message))
        instruction = sut.AssertionInstructionFromChecker(checker,
                                                          lambda env: 'argument to checker')
        # ACT #
        pre_sds_result = instruction.validate_pre_sds(self.environment)
        post_sds_result = instruction.validate_post_setup(self.environment)
        # ASSERT #
        asrt_svh.is_success().apply_with_message(self, pre_sds_result,
                                                 'pre sds validation should succeed')

        assertion = asrt_svh.is_validation_error(asrt.equals(the_error_message))
        assertion.apply_with_message(self, post_sds_result,
                                     'post setup validation should fail')


class CheckerForValidation(sut.Checker):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        raise NotImplementedError('this method should not be used')


class SuccessfulCheckerThatReturnsConstructorArgPlusOne(sut.Checker):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        return arg + 1


class CheckerThatRaisesFailureExceptionIfArgumentIsEqualToOne(sut.Checker):
    ERROR_MESSAGE = 'error message of FAILING checker'

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        if arg == 1:
            raise PfhFailException(self.ERROR_MESSAGE)
        else:
            return arg + 1


class CheckerWithReference(sut.Checker):
    def __init__(self, references: list):
        super().__init__()
        self._references = references

    @property
    def references(self) -> list:
        return self._references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        pass
