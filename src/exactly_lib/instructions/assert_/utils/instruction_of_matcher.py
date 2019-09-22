from typing import Sequence, Callable, TypeVar, Generic

from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.result import pfh
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils.matcher.applier import MatcherApplierResolver
from exactly_lib.test_case_utils.matcher.matcher import Failure
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.hard_error import HardErrorException

T = TypeVar('T')


class Instruction(Generic[T], AssertPhaseInstruction):
    """Makes an instruction of a :class:`Matcher`"""

    def __init__(self,
                 applier: MatcherApplierResolver[None, T],
                 err_msg_constructor: Callable[[Failure[T]], ErrorMessageResolver],
                 ):
        self._applier = applier
        self._err_msg_constructor = err_msg_constructor

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._applier.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        err_msg = self._applier.validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)
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
        err_msg = self._applier.validator.validate_post_sds_if_applicable(environment.path_resolving_environment)
        if err_msg:
            raise HardErrorException(err_msg)

    def _execute(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pfh.PassOrFailOrHardError:
        applier = self._applier.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds)
        failure = applier.apply(None)
        return (
            pfh.new_pfh_fail(self._err_msg_constructor(failure).resolve__tr())
            if failure
            else
            pfh.new_pfh_pass()
        )
