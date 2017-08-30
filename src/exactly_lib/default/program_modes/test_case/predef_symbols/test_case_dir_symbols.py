from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.symbol.value_resolvers import file_ref_resolvers
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util import symbol_table


def __resolver_of(rel_option_type: RelOptionType) -> resolver_structure.NamedElementContainer:
    return resolver_structure.container_of_builtin(
        file_ref_resolvers.resolver_of_rel_option(rel_option_type))


SYMBOL_HOME_CASE = symbol_table.Entry(environment_variables.ENV_VAR_HOME_CASE,
                                      __resolver_of(RelOptionType.REL_HOME_CASE))

SYMBOL_HOME_ACT = symbol_table.Entry(environment_variables.ENV_VAR_HOME_ACT,
                                     __resolver_of(RelOptionType.REL_HOME_ACT))

SYMBOL_ACT = symbol_table.Entry(environment_variables.ENV_VAR_ACT,
                                __resolver_of(RelOptionType.REL_ACT))

SYMBOL_TMP = symbol_table.Entry(environment_variables.ENV_VAR_TMP,
                                __resolver_of(RelOptionType.REL_TMP))

SYMBOL_RESULT = symbol_table.Entry(environment_variables.ENV_VAR_RESULT,
                                   __resolver_of(RelOptionType.REL_RESULT))

ALL = (
    SYMBOL_HOME_CASE,
    SYMBOL_HOME_ACT,
    SYMBOL_ACT,
    SYMBOL_TMP,
    SYMBOL_RESULT,
)
