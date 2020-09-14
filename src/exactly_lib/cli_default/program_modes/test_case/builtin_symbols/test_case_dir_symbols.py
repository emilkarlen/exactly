from exactly_lib.cli.main_program import BuiltinSymbol
from exactly_lib.definitions import formatting
from exactly_lib.definitions.tcds_symbols import SYMBOL_DESCRIPTION
from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.test_case_file_structure import relative_path_options
from exactly_lib.test_case_file_structure import tcds_symbols
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.textformat.textformat_parser import TextParser


def __sdv_of(rel_option_type: RelOptionType) -> sdv_structure.SymbolDependentValue:
    return path_sdvs.of_rel_option(rel_option_type)


def _builtin(symbol_name: str, relativity: RelOptionType) -> BuiltinSymbol:
    tp = TextParser({
        'relativity_option':
            formatting.cli_argument_option_string(
                option_syntax.option_syntax(relative_path_options.REL_OPTIONS_MAP[relativity].option_name)
            )
    })

    return BuiltinSymbol(symbol_name,
                         ValueType.PATH,
                         __sdv_of(relativity),
                         SYMBOL_DESCRIPTION.as_single_line_description_str(symbol_name),
                         tp.section_contents(_DESCRIPTION))


_DESCRIPTION = """\
This is the root directory of paths specified with {relativity_option}. 
"""

SYMBOL_HDS_CASE = _builtin(tcds_symbols.SYMBOL_HDS_CASE,
                           RelOptionType.REL_HDS_CASE)

SYMBOL_HDS_ACT = _builtin(tcds_symbols.SYMBOL_HDS_ACT,
                          RelOptionType.REL_HDS_ACT)

SYMBOL_ACT = _builtin(tcds_symbols.SYMBOL_ACT,
                      RelOptionType.REL_ACT)

SYMBOL_TMP = _builtin(tcds_symbols.SYMBOL_TMP,
                      RelOptionType.REL_TMP)

SYMBOL_RESULT = _builtin(tcds_symbols.SYMBOL_RESULT,
                         RelOptionType.REL_RESULT)

ALL = (
    SYMBOL_HDS_CASE,
    SYMBOL_HDS_ACT,
    SYMBOL_ACT,
    SYMBOL_TMP,
    SYMBOL_RESULT,
)
