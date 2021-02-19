from typing import Optional, Dict, Mapping

from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.util import functional
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ


def optionally_from_proc_exe_settings(x: Optional[InstructionSettings],
                                      pes: ProcessExecutionSettings,
                                      default_environ_getter: DefaultEnvironGetter = get_empty_environ,
                                      ) -> InstructionSettings:
    return (
        InstructionSettings(environ_copy_or_none(pes.environ),
                            default_environ_getter,
                            pes.timeout_in_seconds)
        if x is None
        else
        x
    )


def from_proc_exe_settings(pes: ProcessExecutionSettings,
                           default_environ_getter: DefaultEnvironGetter = get_empty_environ,
                           ) -> InstructionSettings:
    return InstructionSettings(environ_copy_or_none(pes.environ),
                               default_environ_getter,
                               pes.timeout_in_seconds)


def environ_copy_or_none(environ: Optional[Mapping[str, str]]) -> Optional[Dict[str, str]]:
    return functional.map_optional(dict, environ)
