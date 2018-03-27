from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.test_case_utils.external_program.program_with_args import ProgramWithArgsResolver
from exactly_lib.util.process_execution.os_process_execution import ProgramAndArguments


def program_with_args(program: ProgramAndArguments) -> ProgramWithArgsResolver:
    return ProgramWithArgsResolver(string_resolvers.str_constant(program.program),
                                   list_resolvers.from_str_constants(program.arguments))
