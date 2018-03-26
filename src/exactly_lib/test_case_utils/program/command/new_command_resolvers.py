from exactly_lib.symbol.data import list_resolvers, string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case_utils.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.test_case_utils.program.command import new_driver_resolvers as drivers
from exactly_lib.test_case_utils.program.command.new_command_resolver import NewCommandResolver
from exactly_lib.test_case_utils.program.validators import ExistingExecutableFileValidator


def for_shell() -> NewCommandResolver:
    return NewCommandResolver(drivers.NewCommandDriverResolverForShell(),
                              list_resolvers.empty(),
                              ConstantSuccessValidator())


def for_executable_file(executable_file: FileRefResolver) -> NewCommandResolver:
    return NewCommandResolver(drivers.NewCommandDriverResolverForExecutableFile(executable_file),
                              list_resolvers.empty(),
                              ExistingExecutableFileValidator(executable_file))


def for_system_program(program: StringResolver) -> NewCommandResolver:
    return NewCommandResolver(drivers.NewCommandDriverResolverForSystemProgram(program),
                              list_resolvers.empty(),
                              ConstantSuccessValidator())


def for_interpret_file_with_arguments_wip(interpreter: NewCommandResolver,
                                          file_to_interpret: FileRefResolver,
                                          argument_list: ListResolver) -> NewCommandResolver:
    return interpreter.new_with_additional_arguments(_file_interpreter_arguments(file_to_interpret,
                                                                                 argument_list))


def for_source_as_command_line_argument_wip(interpreter: NewCommandResolver,
                                            source: StringResolver) -> NewCommandResolver:
    return interpreter.new_with_additional_arguments(list_resolvers.from_string(source))


def _file_interpreter_arguments(file_to_interpret: FileRefResolver,
                                argument_list: ListResolver) -> ListResolver:
    file_to_interpret_as_string = string_resolvers.from_file_ref_resolver(file_to_interpret)
    return list_resolvers.concat([
        list_resolvers.from_strings([file_to_interpret_as_string]),
        argument_list,
    ])
