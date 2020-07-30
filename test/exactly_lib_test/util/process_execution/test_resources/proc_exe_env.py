from typing import Optional, Dict

from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


def proc_exe_env_for_test(
        timeout_in_seconds: Optional[int] = 30,
        environ: Optional[Dict[str, str]] = None,

) -> ProcessExecutionSettings:
    return ProcessExecutionSettings(
        timeout_in_seconds=timeout_in_seconds,
        environ=environ,
    )
