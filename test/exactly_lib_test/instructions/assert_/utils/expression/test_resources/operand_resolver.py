from exactly_lib.instructions.assert_.utils.condition.comparison_structures import OperandResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib_test.test_resources import actions


def operand_resolver_that(validate_pre_sds=actions.do_nothing,
                          resolve_return_value_action=actions.do_nothing,
                          resolve_initial_action=None,
                          symbol_usages=None,
                          property_name: str = 'test property') -> OperandResolver:
    return _OperandResolverThat(
        validate_pre_sds,
        actions.action_of(resolve_initial_action, resolve_return_value_action),
        [] if symbol_usages is None else symbol_usages,
        property_name
    )


class _OperandResolverThat(OperandResolver):
    def __init__(self,
                 validate_pre_sds,
                 resolve,
                 symbol_usages,
                 property_name: str = 'test property'):
        super().__init__(property_name)

        self._validate_pre_sds = validate_pre_sds
        self._resolve = resolve
        self._symbol_usages = symbol_usages

    @property
    def references(self) -> list:
        return self._symbol_usages

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self._validate_pre_sds(environment)

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep):
        return self._resolve(environment)
