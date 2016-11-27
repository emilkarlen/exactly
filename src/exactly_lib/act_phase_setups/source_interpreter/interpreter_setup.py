import pathlib

from exactly_lib.act_phase_setups.source_interpreter.source_file_management import SourceInterpreterSetup
from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.process_execution.process_execution_settings import Command


def new_for_script_language_setup(script_language_setup: SourceInterpreterSetup) -> ActPhaseSetup:
    return ActPhaseSetup(Constructor(script_language_setup))


def new_for_script_language_handling(script_language_setup: SourceInterpreterSetup) -> ActPhaseHandling:
    return ActPhaseHandling(Constructor(script_language_setup))


class Constructor(parts.Constructor):
    def __init__(self, script_language_setup: SourceInterpreterSetup):
        super().__init__(Parser(),
                         parts.UnconditionallySuccessfulValidator,
                         lambda environment, source_code: Executor(environment, script_language_setup, source_code))
        self.script_language_setup = script_language_setup


class Parser(parts.Parser):
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


class Executor(CommandExecutor):
    FILE_NAME_STEM = 'act-script'

    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 script_language_setup: SourceInterpreterSetup,
                 source_code: str):
        self.script_language_setup = script_language_setup
        self.source_code = source_code

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        script_file_path = self._script_path(script_output_dir_path)
        try:
            with open(str(script_file_path), 'w') as f:
                f.write(self.source_code)
            return sh.new_sh_success()
        except OSError as ex:
            return sh.new_sh_hard_error(str(ex))

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        script_file_path = self._script_path(script_output_dir_path)
        cmd_and_args = self.script_language_setup.command_and_args_for_executing_script_file(str(script_file_path))
        return Command(cmd_and_args, shell=False)

    def _script_path(self,
                     script_output_dir_path: pathlib.Path) -> pathlib.Path:
        base_name = self.script_language_setup.base_name_from_stem(self.FILE_NAME_STEM)
        return script_output_dir_path / base_name
