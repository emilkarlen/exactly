from typing import ContextManager

from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.matcher.impls.run_program import sdv as run_pgm_sdv
from exactly_lib.test_case_utils.matcher.impls.run_program.run_conf import RunConfiguration
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.process_execution import file_ctx_managers
from exactly_lib.util.process_execution.process_executor import ProcessExecutionFile


def sdv(program: ProgramSdv) -> StringMatcherSdv:
    return run_pgm_sdv.sdv(_StringMatcherRunConfiguration(), program)


class _StringMatcherRunConfiguration(RunConfiguration[StringModel]):
    def stdin(self, model: StringModel) -> ContextManager[ProcessExecutionFile]:
        path_of_file_with_model = model.as_file
        return file_ctx_managers.open_file(path_of_file_with_model, 'r')

    def program_for_model(self, matcher_argument_program: Program, model: StringModel) -> Program:
        return Program(
            matcher_argument_program.command,
            matcher_argument_program.stdin,
            IdentityStringTransformer(),
        )
