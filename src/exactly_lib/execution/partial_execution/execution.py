import shutil

from exactly_lib.execution.partial_execution.configuration import TestCase, Configuration
from exactly_lib.execution.partial_execution.impl import executor
from exactly_lib.execution.partial_execution.result import PartialResult
from exactly_lib.execution.tmp_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.util.file_utils import preserved_cwd


def execute(act_phase_handling: ActPhaseHandling,
            test_case: TestCase,
            configuration: Configuration,
            initial_setup_settings: SetupSettingsBuilder,
            sandbox_root_dir_resolver: SandboxRootDirNameResolver,
            is_keep_sandbox: bool) -> PartialResult:
    """
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
            ret_val = executor.execute(configuration,
                                       sandbox_root_dir_resolver,
                                       act_phase_handling,
                                       test_case,
                                       initial_setup_settings)
            return ret_val
    finally:
        if not is_keep_sandbox:
            if ret_val is not None and ret_val.has_sds:
                shutil.rmtree(str(ret_val.sds.root_dir))
