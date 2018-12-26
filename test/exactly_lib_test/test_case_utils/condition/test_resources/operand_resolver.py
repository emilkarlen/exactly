from typing import Sequence, Callable, Optional

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.condition.comparison_structures import OperandResolver, T
from exactly_lib_test.test_resources import actions


def operand_resolver_that(validate_pre_sds=actions.do_nothing__single_arg,
                          resolve_return_value_action=actions.do_nothing,
                          resolve_initial_action=None,
                          symbol_usages: Optional[Sequence[SymbolReference]] = None,
                          property_name: str = 'test property') -> OperandResolver:
    return _OperandResolverThat(
        validate_pre_sds,
        actions.action_of(resolve_initial_action, resolve_return_value_action),
        [] if symbol_usages is None else symbol_usages,
        property_name
    )


class _OperandResolverThat(OperandResolver[T]):
    def __init__(self,
                 validate_pre_sds: Callable[[PathResolvingEnvironmentPreSds], None],
                 resolve: Callable[[PathResolvingEnvironmentPreOrPostSds], T],
                 symbol_usages: Sequence[SymbolReference],
                 property_name: str = 'test property'):
        super().__init__(property_name)

        self._validate_pre_sds = validate_pre_sds
        self._resolve = resolve
        self._symbol_usages = symbol_usages

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_usages

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self._validate_pre_sds(environment)

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> T:
        return self._resolve(environment)
