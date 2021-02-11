from typing import Optional, Mapping

from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


def proc_exe_env_for_test(
        timeout_in_seconds: Optional[int] = 30,
        environ: Optional[Mapping[str, str]] = None,
) -> ProcessExecutionSettings:
    return ProcessExecutionSettings.from_non_immutable(
        timeout_in_seconds=timeout_in_seconds,
        environ=environ,
    )
