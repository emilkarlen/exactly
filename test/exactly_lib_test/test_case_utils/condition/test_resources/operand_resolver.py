from typing import Sequence, Callable, Optional, Generic

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.condition.comparison_structures import OperandResolver, T, OperandValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_resources import actions


def operand_resolver_that(
        validate_pre_sds=actions.do_nothing__single_arg,
        resolve_return_value_action: Callable[[PathResolvingEnvironmentPreOrPostSds], T] = actions.do_nothing,
        resolve_initial_action=None,
        symbol_usages: Optional[Sequence[SymbolReference]] = None,
) -> OperandResolver:
    return _OperandResolverThat(
        validate_pre_sds,
        actions.action_of(resolve_initial_action, resolve_return_value_action),
        [] if symbol_usages is None else symbol_usages,
    )


class _OperandResolverThat(OperandResolver[T]):
    def __init__(self,
                 validate_pre_sds: Callable[[PathResolvingEnvironmentPreSds], None],
                 resolve: Callable[[PathResolvingEnvironmentPreOrPostSds], T],
                 symbol_usages: Sequence[SymbolReference],
                 ):
        self._validate_pre_sds = validate_pre_sds
        self._resolve = resolve
        self._symbol_usages = symbol_usages

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_usages

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self._validate_pre_sds(environment)

    def resolve(self, symbols: SymbolTable) -> OperandValue[T]:
        return _OperandValue(self._resolve, symbols)


class _OperandValue(Generic[T], OperandValue[T]):
    def __init__(self,
                 resolve: Callable[[PathResolvingEnvironmentPreOrPostSds], T],
                 symbols: SymbolTable,
                 ):
        self._resolve = resolve
        self._symbols = symbols

    def value_of_any_dependency(self, tcds: HomeAndSds) -> T:
        env = PathResolvingEnvironmentPreOrPostSds(tcds, self._symbols)
        return self._resolve(env)
