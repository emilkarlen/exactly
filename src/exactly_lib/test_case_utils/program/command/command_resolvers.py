from exactly_lib.symbol.data import list_resolvers, string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case_utils.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.test_case_utils.program.command import new_driver_resolvers as drivers
from exactly_lib.test_case_utils.program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.program.executable_file import ExecutableFileWithArgsResolver
from exactly_lib.test_case_utils.program.validators import ExistingExecutableFileValidator
from exactly_lib.util.process_execution.os_process_execution import ProgramAndArguments


def for_shell() -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForShell(),
                           list_resolvers.empty(),
                           ConstantSuccessValidator())


def for_executable_file(executable_file: FileRefResolver) -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForExecutableFile(executable_file),
                           list_resolvers.empty(),
                           ExistingExecutableFileValidator(executable_file))


def for_system_program(program: StringResolver) -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForSystemProgram(program),
                           list_resolvers.empty(),
                           ConstantSuccessValidator())


def from_old_executable_file(exe_file: ExecutableFileWithArgsResolver) -> CommandResolver:
    return for_executable_file(exe_file.executable_file).new_with_additional_arguments(exe_file.arguments)


def from_program_and_arguments(pgm_and_args: ProgramAndArguments) -> CommandResolver:
    program_resolver = string_resolvers.str_constant(pgm_and_args.program)
    arguments_resolver = list_resolvers.from_str_constants(pgm_and_args.arguments)
    return for_system_program(program_resolver).new_with_additional_arguments(arguments_resolver)


def for_interpret_file_with_arguments_wip(interpreter: CommandResolver,
                                          file_to_interpret: FileRefResolver,
                                          argument_list: ListResolver) -> CommandResolver:
    return interpreter.new_with_additional_arguments(_file_interpreter_arguments(file_to_interpret,
                                                                                 argument_list))


def for_source_as_command_line_argument_wip(interpreter: CommandResolver,
                                            source: StringResolver) -> CommandResolver:
    return interpreter.new_with_additional_arguments(list_resolvers.from_string(source))


def _file_interpreter_arguments(file_to_interpret: FileRefResolver,
                                argument_list: ListResolver) -> ListResolver:
    file_to_interpret_as_string = string_resolvers.from_file_ref_resolver(file_to_interpret)
    return list_resolvers.concat([
        list_resolvers.from_strings([file_to_interpret_as_string]),
        argument_list,
    ])
