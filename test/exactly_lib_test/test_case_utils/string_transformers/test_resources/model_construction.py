from typing import Callable, List

from exactly_lib.type_system.logic.string_transformer import StringTransformerModel

ModelConstructor = Callable[[], StringTransformerModel]


def of_lines(lines: List[str]) -> ModelConstructor:
    def ret_val() -> StringTransformerModel:
        return iter(lines)

    return ret_val
