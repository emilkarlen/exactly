from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.string_transformer import sdvs
from exactly_lib.test_case_utils.string_transformer.impl import tcds_paths_replacement
from exactly_lib.test_case_utils.symbol.custom_symbol import CustomSymbolDocumentation


def replace_env_vars(name: str) -> StringTransformerSdv:
    return sdvs.StringTransformerSdvConstantOfDdv(tcds_paths_replacement.ddv(name))


def replace_tcds_paths_doc() -> CustomSymbolDocumentation:
    return CustomSymbolDocumentation(
        tcds_paths_replacement.SINGLE_LINE_DESCRIPTION,
        tcds_paths_replacement.help_section_contents(),
        tcds_paths_replacement.see_also(),
    )
