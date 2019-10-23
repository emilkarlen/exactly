from typing import Callable, List

from exactly_lib.type_system.logic.string_transformer import StringTransformerModel

ModelConstructor = Callable[[], StringTransformerModel]


def of_lines(lines: List[str]) -> ModelConstructor:
    def ret_val() -> StringTransformerModel:
        return iter(lines)

    return ret_val


def arbitrary_model() -> StringTransformerModel:
    return iter(['string transformer model line'])


def arbitrary_model_constructor() -> ModelConstructor:
    return of_lines(['string transformer model line'])
