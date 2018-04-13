from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.test_case_utils.program.command import arguments_resolvers
from exactly_lib.test_case_utils.program.command import command_resolvers
from exactly_lib.test_case_utils.program.resolvers import command_program_resolver
from exactly_lib.test_case_utils.program.resolvers.command_program_resolver import ProgramResolverForCommand
from exactly_lib_test.test_case_utils.test_resources import command_resolvers as test_command_resolvers


def with_ref_to_exe_file(exe_file: FileRefResolver,
                         arguments: ArgumentsResolver = arguments_resolvers.empty()
                         ) -> ProgramResolverForCommand:
    return command_program_resolver.plain(
        command_resolvers.for_executable_file(exe_file, arguments)
    )


def with_ref_to_program(program: StringResolver,
                        arguments: ArgumentsResolver = arguments_resolvers.empty()
                        ) -> ProgramResolverForCommand:
    return command_program_resolver.plain(
        command_resolvers.for_system_program(program, arguments)
    )


def interpret_py_source_file_that_must_exist(py_source_file: FileRefResolver,
                                             arguments: ArgumentsResolver = arguments_resolvers.empty()
                                             ) -> ProgramResolverForCommand:
    return command_program_resolver.plain(
        test_command_resolvers.for_interpret_py_file_that_must_exist(py_source_file)
    ).new_with_additional_arguments(arguments)


def for_py_source_on_command_line(python_source: str) -> ProgramResolverForCommand:
    return command_program_resolver.plain(
        test_command_resolvers.for_py_source_on_command_line(python_source))
