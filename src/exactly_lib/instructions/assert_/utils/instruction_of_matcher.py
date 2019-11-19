from typing import Sequence, Callable, TypeVar, Generic

from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.result import pfh
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils.matcher.property_matcher import PropertyMatcherSdv
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import Failure

T = TypeVar('T')


class Instruction(Generic[T], AssertPhaseInstruction):
    """Makes an instruction of a :class:`Matcher`"""

    def __init__(self,
                 matcher: PropertyMatcherSdv[None, T],
                 err_msg_constructor: Callable[[Failure[T]], ErrorMessageResolver],
                 ):
        self._matcher = matcher
        self._err_msg_constructor = err_msg_constructor

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._matcher.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        validator = self._matcher.resolve(environment.symbols).validator
        err_msg = validator.validate_pre_sds_if_applicable(environment.hds)
        return svh.new_maybe_svh_validation_error(err_msg)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        try:
            self._validate_post_setup(environment)
            return self._execute(environment)
        except HardErrorException as ex:
            return pfh.new_pfh_hard_error(ex.error)

    def _validate_post_setup(self, environment: i.InstructionEnvironmentForPostSdsStep):
        validator = self._matcher.resolve(environment.symbols).validator
        err_msg = validator.validate_post_sds_if_applicable(environment.tcds)
        if err_msg:
            raise HardErrorException(err_msg)

    def _execute(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pfh.PassOrFailOrHardError:
        matcher = self._matcher.resolve(environment.symbols).value_of_any_dependency(environment.tcds)
        failure = matcher.matches_w_failure(None)
        return (
            pfh.new_pfh_fail(self._err_msg_constructor(failure).resolve__tr())
            if failure
            else
            pfh.new_pfh_pass()
        )
