import pathlib

from exactly_lib.act_phase_setups import utils
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptLanguageSetup
from exactly_lib.act_phase_setups.util.executor_made_of_parts import main as executor_made_of_parts
from exactly_lib.execution.act_phase import ExitCodeOrHardError, \
    ActPhaseHandling
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import HomeAndEds, InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.std import StdFiles


def new_for_script_language_setup(script_language_setup: ScriptLanguageSetup) -> ActPhaseSetup:
    return ActPhaseSetup(Constructor(script_language_setup))


def new_for_script_language_handling(script_language_setup: ScriptLanguageSetup) -> ActPhaseHandling:
    return ActPhaseHandling(Constructor(script_language_setup))


class Constructor(executor_made_of_parts.Constructor):
    def __init__(self, script_language_setup: ScriptLanguageSetup):
        super().__init__(Parser(),
                         executor_made_of_parts.UnconditionallySuccessfulValidator,
                         lambda environment, source_code: Executor(environment, script_language_setup, source_code))
        self.script_language_setup = script_language_setup


class Parser(executor_made_of_parts.Parser):
    def apply(self, act_phase_instructions: list) -> str:
        from exactly_lib.util.string import lines_content
        return lines_content(self._all_source_code_lines(act_phase_instructions))

    @staticmethod
    def _all_source_code_lines(act_phase_instructions) -> list:
        ret_val = []
        for instruction in act_phase_instructions:
            assert isinstance(instruction, ActPhaseInstruction)
            for line in instruction.source_code().lines:
                ret_val.append(line)
        return ret_val


class Executor(executor_made_of_parts.Executor):
    FILE_NAME_STEM = 'act-script'

    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 script_language_setup: ScriptLanguageSetup,
                 source_code: str):
        self.environment = environment
        self.script_language_setup = script_language_setup
        self.source_code = source_code

    def prepare(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        script_file_path = self._script_path(script_output_dir_path)
        try:
            with open(str(script_file_path), 'w') as f:
                f.write(self.source_code)
            return sh.new_sh_success()
        except OSError as ex:
            return sh.new_sh_hard_error(str(ex))

    def execute(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        script_file_path = self._script_path(script_output_dir_path)
        cmd_and_args = self.script_language_setup.command_and_args_for_executing_script_file(str(script_file_path))
        return utils.execute_cmd_and_args(cmd_and_args, std_files,
                                          timeout=self.environment.timeout_in_seconds)

    def _script_path(self,
                     script_output_dir_path: pathlib.Path) -> pathlib.Path:
        base_name = self.script_language_setup.base_name_from_stem(self.FILE_NAME_STEM)
        return script_output_dir_path / base_name
