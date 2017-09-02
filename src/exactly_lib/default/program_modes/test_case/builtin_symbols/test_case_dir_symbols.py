from exactly_lib.default.default_main_program import BuiltinSymbol
from exactly_lib.help.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.symbol.value_resolvers import file_ref_resolvers
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType


def __resolver_of(rel_option_type: RelOptionType) -> resolver_structure.NamedElementResolver:
    return file_ref_resolvers.resolver_of_rel_option(rel_option_type)


SYMBOL_HOME_CASE = BuiltinSymbol(environment_variables.ENV_VAR_HOME_CASE,
                                 __resolver_of(RelOptionType.REL_HOME_CASE),
                                 BuiltinSymbolDocumentation(environment_variables.ENV_VAR_HOME_CASE))

SYMBOL_HOME_ACT = BuiltinSymbol(environment_variables.ENV_VAR_HOME_ACT,
                                __resolver_of(RelOptionType.REL_HOME_ACT),
                                BuiltinSymbolDocumentation(environment_variables.ENV_VAR_HOME_ACT))

SYMBOL_ACT = BuiltinSymbol(environment_variables.ENV_VAR_ACT,
                           __resolver_of(RelOptionType.REL_ACT),
                           BuiltinSymbolDocumentation(environment_variables.ENV_VAR_ACT))

SYMBOL_TMP = BuiltinSymbol(environment_variables.ENV_VAR_TMP,
                           __resolver_of(RelOptionType.REL_TMP),
                           BuiltinSymbolDocumentation(environment_variables.ENV_VAR_TMP))

SYMBOL_RESULT = BuiltinSymbol(environment_variables.ENV_VAR_RESULT,
                              __resolver_of(RelOptionType.REL_RESULT),
                              BuiltinSymbolDocumentation(environment_variables.ENV_VAR_RESULT))

ALL = (
    SYMBOL_HOME_CASE,
    SYMBOL_HOME_ACT,
    SYMBOL_ACT,
    SYMBOL_TMP,
    SYMBOL_RESULT,
)
