from exactly_lib.symbol.data import string_resolvers as csr, list_resolver
from exactly_lib.test_case_utils.sub_proc.program_with_args import ProgramWithArgsResolver
from exactly_lib.util.process_execution.os_process_execution import ProgramAndArguments


def program_with_args(program: ProgramAndArguments) -> ProgramWithArgsResolver:
    return ProgramWithArgsResolver(csr.string_constant(program.program),
                                   list_resolver.from_str_constants(program.arguments))
