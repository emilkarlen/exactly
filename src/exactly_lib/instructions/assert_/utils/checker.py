import itertools
import types

from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import translate_pfh_exception_to_pfh
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh, svh
from exactly_lib.test_case_utils import pre_or_post_validation
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator, \
    PreOrPostSdsSvhValidationErrorValidator


class Checker:
    """
    Checks a value given to the constructor,
    and returns an associated value, that may be
    propagated to the next check in a sequence of checks.

    :raises PfhException: The check is unsuccessful.
    """

    def __init__(self, validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._validator = validator

    @property
    def references(self) -> list:
        return []

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check
              ):
        raise NotImplementedError('abstract method')

    def check_and_return_pfh(self,
                             environment: InstructionEnvironmentForPostSdsStep,
                             os_services: OsServices,
                             value_to_check
                             ) -> pfh.PassOrFailOrHardError:
        return translate_pfh_exception_to_pfh(self.check,
                                              environment,
                                              os_services,
                                              value_to_check)


class SequenceOfChecks(Checker):
    """
    Executes a sequence of checks,
    by executing a sequence of :class:`Checker`s.

    Each checker returns a tuple of values that are given
    to the constructor of the next :class:`Checker`.
    """

    def __init__(self, checkers: list):
        super().__init__(pre_or_post_validation.AndValidator([c.validator for c in checkers]))
        self._checkers = tuple(checkers)
        self._references = list(itertools.chain.from_iterable([c.references for c in checkers]))

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check):
        for checker in self._checkers:
            value_to_check = checker.check(environment, os_services, value_to_check)
        return value_to_check

    @property
    def references(self) -> list:
        return self._references


class AssertionInstructionFromChecker(AssertPhaseInstruction):
    """ An :class:`AssertPhaseInstruction` in terms of a :class:`Checker`'
    """

    def __init__(self,
                 checker: Checker,
                 get_argument_to_checker: types.FunctionType,
                 ):
        """
        :param get_argument_to_checker: Returns the argument to give to
        the checker, given a :class:`InstructionEnvironmentForPostSdsStep`
        """
        self._checker = checker
        self._get_argument_to_checker = get_argument_to_checker
        self._validator = PreOrPostSdsSvhValidationErrorValidator(checker.validator)

    def symbol_usages(self) -> list:
        return self._checker.references

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_post_sds_if_applicable(environment.path_resolving_environment)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        argument_to_checker = self._get_argument_to_checker(environment)
        return self._checker.check_and_return_pfh(environment, os_services,
                                                  argument_to_checker)
