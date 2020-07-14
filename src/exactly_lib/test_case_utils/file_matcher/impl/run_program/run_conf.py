from typing import ContextManager

from exactly_lib.test_case_utils.file_matcher.impl.run_program.arguments_generator import ArgumentsGenerator
from exactly_lib.test_case_utils.matcher.impls.run_program.run_conf import RunConfiguration
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.program.process_execution import command
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.util.process_execution import file_ctx_managers
from exactly_lib.util.process_execution.process_executor import ProcessExecutionFile


class FileMatcherRunConfiguration(RunConfiguration[FileMatcherModel]):
    def __init__(self, args_generator: ArgumentsGenerator):
        self._args_generator = args_generator

    def stdin(self, model: FileMatcherModel) -> ContextManager[ProcessExecutionFile]:
        return file_ctx_managers.dev_null()

    def program_for_model(self, matcher_argument_program: Program, model: FileMatcherModel) -> Program:
        original_command = matcher_argument_program.command
        arguments = self._args_generator.generate(original_command.arguments, str(model.path.primitive))
        command_for_model = command.Command(
            original_command.driver,
            arguments
        )
        return Program(
            command_for_model,
            matcher_argument_program.stdin,
            IdentityStringTransformer(),
        )
