import shutil
from typing import Tuple, Callable

from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution.configuration import TestCase, ConfPhaseValues
from exactly_lib.execution.partial_execution.impl import executor
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.test_case.phases.act.actor import Actor, ActionToCheck
from exactly_lib.test_case.phases.environ import OptionalEnvVarsDict
from exactly_lib.test_case.phases.setup.settings_handler import SetupSettingsHandler
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable

MkSetupSettingsHandler = Callable[[OptionalEnvVarsDict], SetupSettingsHandler]


def parse_atc_and_validate_symbols(actor: NameAndValue[Actor],
                                   predefined_symbols: SymbolTable,
                                   test_case: TestCase,
                                   ) -> Tuple[ActionToCheck, SymbolTable]:
    """
    :raises PhaseStepFailureException
    """
    return executor.parse_atc_and_validate_symbols(actor,
                                                   predefined_symbols,
                                                   test_case)


def execute(test_case: TestCase,
            full_exe_input_conf: ExecutionConfiguration,
            conf_phase_values: ConfPhaseValues,
            setup_handler: MkSetupSettingsHandler,
            is_keep_sandbox: bool) -> PartialExeResult:
    """
    Part of execution that is independent of the "status" (SKIP, PASS, FAIL, ...)

    Takes care of construction of the Sandbox directory structure, including
    the root directory, and executes a given Test Case in this directory.

    Preserves Current Working Directory.

    Perhaps the test case should be executed in a sub process, so that
    Environment Variables and Current Working Directory of the process that executes
    the main program is not modified.

    The responsibility of this method is not the most natural!!
    Please refactor if a more natural responsibility evolves!
    """
    ret_val = None
    try:
        with preserved_cwd():
            ret_val = executor.execute(
                executor.Configuration(full_exe_input_conf,
                                       conf_phase_values,
                                       setup_handler),
                test_case,
            )
            return ret_val
    finally:
        if not is_keep_sandbox:
            if ret_val is not None and ret_val.has_sds:
                shutil.rmtree(str(ret_val.sds.root_dir),
                              ignore_errors=True)
