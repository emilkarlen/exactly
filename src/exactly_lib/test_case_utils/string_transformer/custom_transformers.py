from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.test_case_utils.string_transformer import resolvers
from exactly_lib.test_case_utils.string_transformer.impl import env_vars_replacement, case_converters
from exactly_lib.test_case_utils.symbol.custom_symbol import CustomSymbolDocumentation
from exactly_lib.util.textformat.structure import document


def to_upper_case(name: str) -> StringTransformerResolver:
    return resolvers.StringTransformerConstant(case_converters.ToUpperCaseStringTransformer(name))


def to_lower_case(name: str) -> StringTransformerResolver:
    return resolvers.StringTransformerConstant(case_converters.ToLowerCaseStringTransformer(name))


def replace_env_vars(name: str) -> StringTransformerResolver:
    return resolvers.StringTransformerConstantOfDdv(env_vars_replacement.ddv(name))


def to_upper_case_doc() -> CustomSymbolDocumentation:
    return CustomSymbolDocumentation(
        'Converts all cased characters to uppercase',
        document.empty_section_contents(),
    )


def to_lower_case_doc() -> CustomSymbolDocumentation:
    return CustomSymbolDocumentation(
        'Converts all cased characters to lowercase',
        document.empty_section_contents(),
    )


def replace_env_vars_doc() -> CustomSymbolDocumentation:
    return CustomSymbolDocumentation(
        env_vars_replacement.SINGLE_LINE_DESCRIPTION,
        env_vars_replacement.with_replaced_env_vars_help(),
        env_vars_replacement.with_replaced_env_vars_see_also(),
    )
