from exactly_lib.cli.main_program import BuiltinSymbol
from exactly_lib.help_texts.environment_variables import ENVIRONMENT_VARIABLE_DESCRIPTION
from exactly_lib.symbol import resolver_structure
from exactly_lib.symbol.data.value_resolvers import file_ref_resolvers
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


def __resolver_of(rel_option_type: RelOptionType) -> resolver_structure.SymbolValueResolver:
    return file_ref_resolvers.resolver_of_rel_option(rel_option_type)


_TEXT_PARSER = TextParser()


def _builtin(variable_name: str, relativity: RelOptionType) -> BuiltinSymbol:
    return BuiltinSymbol(variable_name,
                         __resolver_of(relativity),
                         ENVIRONMENT_VARIABLE_DESCRIPTION.as_single_line_description_str(variable_name),
                         SectionContents([]))


SYMBOL_HOME_CASE = _builtin(environment_variables.ENV_VAR_HOME_CASE,
                            RelOptionType.REL_HOME_CASE)

SYMBOL_HOME_ACT = _builtin(environment_variables.ENV_VAR_HOME_ACT,
                           RelOptionType.REL_HOME_ACT)

SYMBOL_ACT = _builtin(environment_variables.ENV_VAR_ACT,
                      RelOptionType.REL_ACT)

SYMBOL_TMP = _builtin(environment_variables.ENV_VAR_TMP,
                      RelOptionType.REL_TMP)

SYMBOL_RESULT = _builtin(environment_variables.ENV_VAR_RESULT,
                         RelOptionType.REL_RESULT)

ALL = (
    SYMBOL_HOME_CASE,
    SYMBOL_HOME_ACT,
    SYMBOL_ACT,
    SYMBOL_TMP,
    SYMBOL_RESULT,
)
