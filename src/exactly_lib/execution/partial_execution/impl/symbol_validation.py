from typing import Callable

from exactly_lib.execution import phase_step
from exactly_lib.execution.impl.phase_step_execution import PhaseStepFailureResultConstructor, \
    execute_action_and_catch_internal_error_exception, run_instructions_phase_step
from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo
from exactly_lib.execution.impl.symbol_validation import validate_symbol_usages
from exactly_lib.execution.partial_execution.configuration import TestCase
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.execution.result import PhaseStepFailureException, ExecutionFailureStatus
from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case.phases.act.actor import ActionToCheck
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.symbol_table import SymbolTable


class SymbolsValidator:
    def __init__(self,
                 initial_symbols: SymbolTable,
                 test_case: TestCase,
                 action_to_check: ActionToCheck,
                 mk_atc_failure_con: Callable[[PhaseStep], PhaseStepFailureResultConstructor],
                 ):
        self._symbols = initial_symbols.copy()
        self._test_case = test_case
        self._action_to_check = action_to_check
        self._mk_atc_failure_con = mk_atc_failure_con

        self._validation_executor = ValidateSymbolsExecutor(self._symbols)

    @property
    def output(self) -> SymbolTable:
        """
        :return: The initial symbols table, with symbol definitions validated by
        validate, added.
        """
        return self._symbols

    def validate(self):
        """
        :raises PhaseStepFailureException
        """
        test_case = self._test_case

        self._validate(phase_step.SETUP__VALIDATE_SYMBOLS,
                       test_case.setup_phase)
        self._validate_atc()
        self._validate(phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS,
                       test_case.before_assert_phase)
        self._validate(phase_step.ASSERT__VALIDATE_SYMBOLS,
                       test_case.assert_phase)
        self._validate(phase_step.CLEANUP__VALIDATE_SYMBOLS,
                       test_case.cleanup_phase)

    def _validate_atc(self):
        failure_con = self._mk_atc_failure_con(phase_step.ACT__VALIDATE_SYMBOLS)

        def action():
            res = self._validation_executor.apply(self._action_to_check)
            if res is not None:
                raise PhaseStepFailureException(
                    failure_con.apply(ExecutionFailureStatus(res.status.value),
                                      FailureDetails.new_message(res.error_message))
                )

        execute_action_and_catch_internal_error_exception(action, failure_con)

    def _validate(self,
                  step: PhaseStep,
                  phase_contents: SectionContents):
        run_instructions_phase_step(step,
                                    self._validation_executor,
                                    phase_contents)


class ValidateSymbolsExecutor(ControlledInstructionExecutor):
    def __init__(self, symbols: SymbolTable):
        self.__symbols = symbols

    def apply(self, symbol_user: SymbolUser) -> PartialInstructionControlledFailureInfo:
        return validate_symbol_usages(symbol_user.symbol_usages(),
                                      self.__symbols)
