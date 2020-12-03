from typing import ContextManager

from exactly_lib.impls.types.matcher.impls.run_program import sdv as run_pgm_sdv
from exactly_lib.impls.types.matcher.impls.run_program.run_conf import RunConfiguration
from exactly_lib.impls.types.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.std import ProcessExecutionFile
from exactly_lib.util.process_execution import file_ctx_managers


def sdv(program: ProgramSdv) -> StringMatcherSdv:
    return run_pgm_sdv.sdv(_StringMatcherRunConfiguration(), program)


class _StringMatcherRunConfiguration(RunConfiguration[StringSource]):
    def stdin(self, model: StringSource) -> ContextManager[ProcessExecutionFile]:
        path_of_file_with_model = model.as_file
        return file_ctx_managers.open_file(path_of_file_with_model, 'r')

    def program_for_model(self, matcher_argument_program: Program, model: StringSource) -> Program:
        return Program(
            matcher_argument_program.command,
            matcher_argument_program.stdin,
            IdentityStringTransformer(),
        )
