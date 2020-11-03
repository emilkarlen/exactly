from exactly_lib.impls.actors.source_interpreter import parser as pa
from exactly_lib.impls.actors.util.actor_from_parts.command_executor import OsProcessExecutor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv


class Executor(OsProcessExecutor):
    def __init__(self,
                 os_services: OsServices,
                 object_to_execute: pa.InterpreterAndSourceInfo,
                 act_source_file_base_name: str,
                 ):
        super().__init__(os_services)
        self.act_source_file_base_name = act_source_file_base_name
        self.object_to_execute = object_to_execute
        self.source_file_path = None

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                ):
        self._set_source_file_path(environment)
        resolving_env = environment.path_resolving_environment_pre_or_post_sds
        source_code = self.object_to_execute.source.resolve_value_of_any_dependency(resolving_env)
        try:
            with self.source_file_path.open('w') as f:
                f.write(source_code)
        except OSError as ex:
            self._hard_error(ex)

    def _set_source_file_path(self, environment: InstructionEnvironmentForPostSdsStep):
        root_dir = environment.tmp_dir__path_access.paths_access.new_path_as_existing_dir()
        self.source_file_path = root_dir / self.act_source_file_base_name

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> CommandSdv:
        return self.object_to_execute.interpreter.new_with_additional_arguments(
            ArgumentsSdv(list_sdvs.from_str_constants([str(self.source_file_path)]))
        )

    @staticmethod
    def _hard_error(ex: Exception):
        from exactly_lib.test_case.hard_error import HardErrorException
        from exactly_lib.common.report_rendering.parts.failure_details import FailureDetailsRenderer
        from exactly_lib.test_case.result.failure_details import FailureDetails
        from exactly_lib.execution.phase_step import ACT__PREPARE

        msg = 'Error in {}'.format(ACT__PREPARE.step)
        raise HardErrorException(
            FailureDetailsRenderer(FailureDetails.new_exception(ex, message=msg))
        )
