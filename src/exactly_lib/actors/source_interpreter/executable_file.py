from exactly_lib.actors.source_interpreter import parser_and_executor as pa
from exactly_lib.actors.source_interpreter.source_file_management import SourceInterpreterSetup
from exactly_lib.actors.util.executor_made_of_parts import parts
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case.actor import AtcOsProcessExecutor, Actor
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.program.command import command_sdvs


def actor(setup: SourceInterpreterSetup) -> Actor:
    return parts.ActorFromParts(
        pa.Parser(),
        parts.UnconditionallySuccessfulValidatorConstructor(),
        _ExecutorConstructor(setup),
    )


class ActSourceFileNameGeneratorForSourceInterpreterSetup(pa.ActSourceFileNameGenerator):
    FILE_NAME_STEM = 'act-source'

    def __init__(self,
                 setup: SourceInterpreterSetup):
        self.setup = setup

    def base_name(self) -> str:
        return self.setup.base_name_from_stem(self.FILE_NAME_STEM)


class _ExecutorConstructor(parts.ExecutorConstructor[pa.SourceInfo]):
    def __init__(self, setup: SourceInterpreterSetup):
        self._setup = setup

    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_process_executor: AtcOsProcessExecutor,
                  object_to_execute: pa.SourceInfo) -> parts.Executor:
        return _Executor(
            os_process_executor,
            self._setup,
            object_to_execute)


class _Executor(pa.ExecutorBase):
    def __init__(self,
                 os_process_executor: AtcOsProcessExecutor,
                 script_language_setup: SourceInterpreterSetup,
                 source_info: pa.SourceInfo):
        super().__init__(os_process_executor,
                         ActSourceFileNameGeneratorForSourceInterpreterSetup(script_language_setup),
                         source_info)
        self.script_language_setup = script_language_setup

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> CommandSdv:
        pgm_and_args = self.script_language_setup.command_and_args_for_executing_script_file(
            str(self.source_file_path)
        )
        return command_sdvs.for_system_program__from_pgm_and_args(pgm_and_args)
