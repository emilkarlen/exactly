import unittest

from exactly_lib.instructions.assert_.utils import checker as sut
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.resolver_structure import ElementType
from exactly_lib.named_element.restriction import ElementTypeRestriction
from exactly_lib.test_case import os_services as oss
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_rs
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_element_type_restriction
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestChecker),
        unittest.makeSuite(TestSequence),
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

    def test_WHEN_a_failing_checker_SHOULD_stop_execution(self):
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

    def test_references_from_all_checkers_SHOULD_be_reported(self):
        # ARRANGE #
        ref_1_info = NameAndValue('ref 1', ElementType.FILE_SELECTOR)
        ref_2_info = NameAndValue('ref 2', ElementType.SYMBOL)

        ref_1 = NamedElementReference(ref_1_info.name,
                                      ElementTypeRestriction(ref_1_info.value))
        ref_2 = NamedElementReference(ref_2_info.name,
                                      ElementTypeRestriction(ref_2_info.value))

        expected_references = asrt.matches_sequence([
            asrt_rs.matches_reference(asrt.equals(ref_1_info.name),
                                      is_element_type_restriction(ref_1_info.value)),
            asrt_rs.matches_reference(asrt.equals(ref_2_info.name),
                                      is_element_type_restriction(ref_2_info.value)),
        ])

        checker = sut.SequenceOfChecks([CheckerWithReference([ref_1]),
                                        CheckerWithReference([]),
                                        CheckerWithReference([ref_2])])
        # ACT #
        actual = checker.references
        # ASSERT #
        expected_references.apply_without_message(self, actual)


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
        self._references = references

    @property
    def references(self) -> list:
        return self._references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              arg: int):
        pass
