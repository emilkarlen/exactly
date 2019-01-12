from typing import List

from exactly_lib.cli.definitions.common_cli_options import SYMBOL_COMMAND


def arguments(symbol_arguments: List[str]) -> List[str]:
    return [SYMBOL_COMMAND] + symbol_arguments
