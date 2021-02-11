from typing import Optional, Dict, Mapping

from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


def optionally_from_proc_exe_settings(x: Optional[InstructionSettings],
                                      pes: ProcessExecutionSettings) -> InstructionSettings:
    return (
        InstructionSettings(environ_copy_or_none(pes.environ))
        if x is None
        else
        x
    )


def from_proc_exe_settings(pes: ProcessExecutionSettings) -> InstructionSettings:
    return InstructionSettings(environ_copy_or_none(pes.environ))


def environ_copy_or_none(environ: Optional[Mapping[str, str]]) -> Optional[Dict[str, str]]:
    return (
        None
        if environ is None
        else dict(environ)
    )
