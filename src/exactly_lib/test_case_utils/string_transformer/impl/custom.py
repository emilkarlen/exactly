from abc import ABC

from exactly_lib.type_system.logic.string_transformer import StringTransformer


class CustomStringTransformer(StringTransformer, ABC):
    """
    Base class for built in custom transformers.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return str(type(self))
