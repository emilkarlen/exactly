"""
Utilities introduced while refactoring the act phase.

The feeling is that these will be removed, or moved, after the refactoring is done.
"""
import pathlib

from exactly_lib.execution.act_phase import ActSourceExecutor, ActSourceAndExecutor, SourceSetup, ExitCodeOrHardError, \
    ActSourceAndExecutorConstructor
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilderForStatementLines
from exactly_lib.test_case.phases.common import HomeAndEds, GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles


class ActSourceParserUsingActSourceExecutor(ActSourceAndExecutorConstructor):
    def __init__(self,
                 adapted: ActSourceExecutor):
        self.adapted = adapted

    def apply(self,
              environment: GlobalEnvironmentForPreEdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        """
        :param act_phase_instructions: [ActPhaseInstruction]
        """
        return ActSourceAndExecutorAdapterForActSourceExecutor(act_phase_instructions,
                                                               self.adapted)


class ActSourceAndExecutorAdapterForActSourceExecutor(ActSourceAndExecutor):
    """
    Adapter used while refactoring act phase handling.
    """

    def __init__(self,
                 act_phase_instructions: list,
                 adapted: ActSourceExecutor):
        self.adapted = adapted
        self.source_builder = ActSourceBuilderForStatementLines()
        for instruction in act_phase_instructions:
            assert isinstance(instruction, ActPhaseInstruction)
            self.source_builder.raw_script_statements(instruction.source_code().lines)

    def validate_pre_eds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return self.adapted.validate_pre_eds(self.source_builder, home_dir_path)

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
