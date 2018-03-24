from typing import Sequence, List

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import CmdAndArgsResolverForProgramAndArguments


class ConstantCmdAndArgsResolverForProgramAndArguments(CmdAndArgsResolverForProgramAndArguments):
    def __init__(self, pgm_and_args_resolver: ListResolver):
        self.__pgm_and_args_resolver = pgm_and_args_resolver

    def resolve_program_and_arguments(self, environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        value = self.__pgm_and_args_resolver.resolve(environment.symbols)
        return value.value_of_any_dependency(environment.home_and_sds)

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self.__pgm_and_args_resolver.references
