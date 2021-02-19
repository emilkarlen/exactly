from typing import Dict, Optional

from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.util.symbol_table import SymbolTable


def get_empty_environ() -> Dict[str, str]:
    return dict()


def new_empty() -> PredefinedProperties:
    return new_w_empty_defaults()


def new_w_empty_defaults(
        default_environ_getter: DefaultEnvironGetter = get_empty_environ,
        environ: Optional[Dict[str, str]] = None,
        timeout_in_seconds: Optional[int] = None,
        symbols: Optional[SymbolTable] = None,

) -> PredefinedProperties:
    return PredefinedProperties(
        default_environ_getter=default_environ_getter,
        environ=environ,
        timeout_in_seconds=timeout_in_seconds,
        predefined_symbols=symbols,
    )
