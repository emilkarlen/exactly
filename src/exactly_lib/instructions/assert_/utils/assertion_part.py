from abc import ABC, abstractmethod
from typing import Sequence, Any, Callable, TypeVar, Generic, List, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.instructions.utils import logic_type_resolving_helper
from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference, \
    references_from_objects_with_symbol_references
from exactly_lib.symbol.sdv_validation import SdvValidator
from exactly_lib.symbol.sdv_with_validation import ObjectWithSymbolReferencesAndSdvValidation
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import pfh, svh
from exactly_lib.test_case.result.pfh import PassOrFailOrHardErrorEnum
from exactly_lib.test_case_utils.pfh_exception import translate_pfh_exception_to_pfh
from exactly_lib.test_case_utils.validators import PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class AssertionPart(Generic[A, B], ObjectWithSymbolReferencesAndSdvValidation, ABC):
    """
    A part of an assertion instruction that
    executes one part of the whole assertion.

    Checks a value given to the constructor,
    and returns an associated value, that may be
    propagated to the next check in a sequence of checks.

    :raises PfhException: The check is unsuccessful.
    """

    def __init__(self, validator: SdvValidator = sdv_validation.ConstantSuccessSdvValidator()):
        self._validator = validator

    @property
    def validator(self) -> SdvValidator:
        return self._validator

    @abstractmethod
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check: A
              ) -> B:
        """
        :param value_to_check: A value that the concrete assertion parts.
        knows what to do with - either as being the object or check,
        or helper information.

        :return: An optional object that may be useful for further assertion parts.

        :raises PfhException: Indicates that the assertion part does not PASS.
        """
        pass

    def check_and_return_pfh(self,
                             environment: InstructionEnvironmentForPostSdsStep,
                             os_services: OsServices,
                             value_to_check: A
                             ) -> pfh.PassOrFailOrHardError:
        return translate_pfh_exception_to_pfh(self.check,
                                              environment,
                                              os_services,
                                              value_to_check)


class IdentityAssertionPart(Generic[A], AssertionPart[A, A]):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check: A
              ) -> A:
        self._check(environment, os_services, value_to_check)
        return value_to_check

    @abstractmethod
    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               os_services: OsServices,
               value_to_check: A
               ):
        pass


class IdentityAssertionPartWithValidationAndReferences(Generic[A], IdentityAssertionPart[A]):
    def __init__(self,
                 validator: SdvValidator,
                 references: Sequence[SymbolReference]):
        super().__init__(validator)
        self._references = references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               os_services: OsServices,
               value_to_check: A
               ):
        pass


class SequenceOfCooperativeAssertionParts(AssertionPart[A, B]):
    """
    Executes a sequence of assertions,
    by executing a sequence of :class:`AssertionPart`s.

    Each assertion part returns a value that is given
    to the constructor of the next :class:`AssertionPart`.
    """

    def __init__(self, assertion_parts: Sequence[AssertionPart]):
        super().__init__(sdv_validation.AndSdvValidator([c.validator for c in assertion_parts]))
        self._assertion_parts = tuple(assertion_parts)
        self._references = references_from_objects_with_symbol_references(assertion_parts)

    @property
    def parts(self) -> List[AssertionPart]:
        return list(self._assertion_parts)

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check: A) -> B:
        for assertion_part in self._assertion_parts:
            value_to_check = assertion_part.check(environment, os_services, value_to_check)
        return value_to_check

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


def compose(first: AssertionPart[A, B],
            second: AssertionPart[B, C]) -> SequenceOfCooperativeAssertionParts[A, C]:
    return SequenceOfCooperativeAssertionParts([first, second])


def compose_with_sequence(first: SequenceOfCooperativeAssertionParts[A, B],
                          second: AssertionPart[B, C]) -> SequenceOfCooperativeAssertionParts[A, C]:
    """
    "Flat"/weird composition.

    For getting "flat" list of validators.  Do not remember why this is nice, though.
    """
    return SequenceOfCooperativeAssertionParts(first.parts + [second])


class AssertionInstructionFromAssertionPart(Generic[A], AssertPhaseInstruction):
    """ An :class:`AssertPhaseInstruction` in terms of a :class:`AssertionPart`'
    """

    def __init__(self,
                 assertion_part: AssertionPart[A, Any],
                 get_argument_to_part: Callable[[InstructionEnvironmentForPostSdsStep], A],
                 failure_message_header:
                 Optional[Callable[[FullResolvingEnvironment], Renderer[MajorBlock]]] = None,
                 ):
        """
        :param get_argument_to_part: Returns the argument to give to
        the assertion part
        """
        self._assertion_part = assertion_part
        self._get_argument_to_assertion_part = get_argument_to_part
        self._validator = PreOrPostSdsSvhValidationErrorValidator(assertion_part.validator)
        self._failure_message_header = failure_message_header

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._assertion_part.references

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        post_sds_validation_result = self._assertion_part.validator.validate_post_sds_if_applicable(
            environment.path_resolving_environment
        )
        if post_sds_validation_result is not None:
            return pfh.new_pfh_hard_error(post_sds_validation_result)

        return self._execute(environment, os_services)

    def _execute(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices) -> pfh.PassOrFailOrHardError:
        argument_to_checker = self._get_argument_to_assertion_part(environment)
        result = self._assertion_part.check_and_return_pfh(environment,
                                                           os_services,
                                                           argument_to_checker)

        if result.status is PassOrFailOrHardErrorEnum.FAIL:
            return self._failure(os_services, environment, result.failure_message)
        else:
            return result

    def _failure(self,
                 os_services: OsServices,
                 environment: InstructionEnvironmentForPostSdsStep,
                 err_msg_from_part: TextRenderer
                 ) -> pfh.PassOrFailOrHardError:
        err_msg = err_msg_from_part
        resolving_env = logic_type_resolving_helper.full_resolving_env_for_instruction_env(
            os_services,
            environment
        )
        if self._failure_message_header:
            err_msg = rend_comb.PrependR(
                self._failure_message_header(resolving_env),
                err_msg_from_part,
            )

        return pfh.new_pfh_fail(err_msg)
