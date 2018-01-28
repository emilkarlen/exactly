import types
from typing import Sequence

from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import translate_pfh_exception_to_pfh
from exactly_lib.symbol.object_with_symbol_references import ObjectWithSymbolReferences, \
    references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh, svh
from exactly_lib.test_case_utils import pre_or_post_validation
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator, \
    PreOrPostSdsSvhValidationErrorValidator


class AssertionPart(ObjectWithSymbolReferences):
    """
    A part of an assertion instruction that
    executes one part of the whole assertion.

    Checks a value given to the constructor,
    and returns an associated value, that may be
    propagated to the next check in a sequence of checks.

    :raises PfhException: The check is unsuccessful.
    """

    def __init__(self, validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._validator = validator

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check
              ):
        """
        :param value_to_check: A value that the concrete assertion parts.
        knows what to do with - either as being the object or check,
        or helper information.

        :return: An optional object that may be useful for further assertion parts.

        :raises PfhException: Indicates that the assertion part does not PASS.
        """
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


class SequenceOfCooperativeAssertionParts(AssertionPart):
    """
    Executes a sequence of assertions,
    by executing a sequence of :class:`AssertionPart`s.

    Each assertion part returns a value that is given
    to the constructor of the next :class:`AssertionPart`.
    """

    def __init__(self, assertion_parts: list):
        super().__init__(pre_or_post_validation.AndValidator([c.validator for c in assertion_parts]))
        self._assertion_parts = tuple(assertion_parts)
        self._references = references_from_objects_with_symbol_references(assertion_parts)

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check):
        for assertion_part in self._assertion_parts:
            value_to_check = assertion_part.check(environment, os_services, value_to_check)
        return value_to_check

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class AssertionInstructionFromAssertionPart(AssertPhaseInstruction):
    """ An :class:`AssertPhaseInstruction` in terms of a :class:`AssertionPart`'
    """

    def __init__(self,
                 assertion_part: AssertionPart,
                 get_argument_to_checker: types.FunctionType,
                 ):
        """
        :param get_argument_to_checker: Returns the argument to give to
        the assertion part, given a :class:`InstructionEnvironmentForPostSdsStep`
        """
        self._assertion_part = assertion_part
        self._get_argument_to_assertion_part = get_argument_to_checker
        self._validator = PreOrPostSdsSvhValidationErrorValidator(assertion_part.validator)

    def symbol_usages(self) -> list:
        return self._assertion_part.references

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
        argument_to_checker = self._get_argument_to_assertion_part(environment)
        return self._assertion_part.check_and_return_pfh(environment, os_services,
                                                         argument_to_checker)
