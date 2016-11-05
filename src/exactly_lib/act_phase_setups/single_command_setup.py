import pathlib

from exactly_lib.act_phase_setups import utils
from exactly_lib.act_phase_setups.util.executor_made_of_parts import main as executor_made_of_parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntaxSplitAccordingToShellSyntax
from exactly_lib.execution.act_phase import ExitCodeOrHardError
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.phases.common import HomeAndEds, InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(Constructor())


class Constructor(executor_made_of_parts.Constructor):
    def __init__(self):
        super().__init__(ParserForSingleLineUsingStandardSyntaxSplitAccordingToShellSyntax(),
                         Validator,
                         Executor)


class Validator(executor_made_of_parts.Validator):
    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 cmd_and_args: list):
        self.cmd_and_args = cmd_and_args

    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        cmd = self.cmd_and_args[0]
        cmd_path = pathlib.Path(cmd)
        if cmd_path.is_absolute():
            if not cmd_path.exists():
                return svh.new_svh_validation_error('File does not exist: ' + cmd)
        else:
            cmd_abs_path = home_dir_path / cmd
            if not cmd_abs_path.exists():
                return svh.new_svh_validation_error('Not a file relative home-dir: ' + str(cmd_abs_path))
        return svh.new_svh_success()

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class Executor(executor_made_of_parts.Executor):
    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 cmd_and_args: list):
        self.environment = environment
        self.cmd_and_args = cmd_and_args

    def prepare(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        cmd = self.cmd_and_args[0]
        cmd_path = pathlib.Path(cmd)
        if not cmd_path.is_absolute():
            cmd_path = home_and_eds.home_dir_path / cmd_path
            self.cmd_and_args[0] = str(cmd_path)
        return utils.execute_cmd_and_args(self.cmd_and_args,
                                          std_files,
                                          timeout=self.environment.timeout_in_seconds)
