from typing import List

from exactly_lib.impls.types.matcher.impls.run_program import sdv as run_pgm_sdv
from exactly_lib.impls.types.matcher.impls.run_program.run_conf import RunConfiguration
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_source.string_source import StringSource


def sdv(program: ProgramSdv) -> StringMatcherSdv:
    return run_pgm_sdv.sdv(_StringMatcherRunConfiguration(), program)


class _StringMatcherRunConfiguration(RunConfiguration[StringSource]):
    def additional_stdin(self, model: StringSource) -> List[StringSource]:
        return [model]

    def program_for_model(self, matcher_argument_program: Program, model: StringSource) -> Program:
        return Program(
            matcher_argument_program.command,
            matcher_argument_program.stdin,
            (),
        )
