"""
Utilities introduced while refactoring the act phase.

The feeling is that these will be removed, or moved, after the refactoring is done.
"""
import pathlib

from exactly_lib.execution.act_phase import ActSourceExecutor, ActSourceAndExecutor, SourceSetup, ExitCodeOrHardError, \
    ActSourceParser
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilderForStatementLines
from exactly_lib.test_case.phases.common import HomeAndEds, GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.std import StdFiles


class ActSourceParserUsingActSourceExecutor(ActSourceParser):
    def __init__(self,
                 adapted: ActSourceExecutor):
        self.adapted = adapted

    def apply(self,
              environment: GlobalEnvironmentForPreEdsStep,
              act_phase: ActPhaseInstruction) -> ActSourceAndExecutor:
        return ActSourceAndExecutorAdapterForActSourceExecutor(act_phase.source_code(environment),
                                                               self.adapted)


class ActSourceAndExecutorAdapterForActSourceExecutor(ActSourceAndExecutor):
    """
    Adapter used while refactoring act phase handling.
    """

    def __init__(self,
                 source: LineSequence,
                 adapted: ActSourceExecutor):
        self.adapted = adapted
        self.source_builder = ActSourceBuilderForStatementLines()
        self.source_builder.raw_script_statements(source.lines)

    def validate_pre_eds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        raise NotImplementedError('Wrapped object does not have a corresponding method: validate_pre_eds')

    def validate_post_setup(self,
                            home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        return self.adapted.validate(home_and_eds.home_dir_path, self.source_builder)

    def prepare(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return self.adapted.prepare(SourceSetup(self.source_builder, script_output_dir_path),
                                    home_and_eds.home_dir_path,
                                    home_and_eds.eds)

    def execute(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self.adapted.execute(SourceSetup(self.source_builder, script_output_dir_path),
                                    home_and_eds.home_dir_path,
                                    home_and_eds.eds,
                                    std_files)
