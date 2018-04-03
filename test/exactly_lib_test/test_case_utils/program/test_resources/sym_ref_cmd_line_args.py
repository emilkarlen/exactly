from typing import Sequence

from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer, Stringable


def sym_ref_cmd_line(symbol_name: Stringable, arguments: Sequence[Stringable] = ()) -> ArgumentElementRenderer:
    return ab.sequence([symbol_name] + list(arguments))
