from abc import ABC, abstractmethod

from exactly_lib.type_val_prims.description.tree_structured import WithNameAndNodeDescription
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class StringTransformer(WithNameAndNodeDescription, ABC):
    """
    Transforms a sequence of lines, where each line is a string.
    """

    @property
    def is_identity_transformer(self) -> bool:
        """
        Tells if this transformer is the identity transformer
        """
        return False

    @abstractmethod
    def transform(self, model: StringSource) -> StringSource:
        pass

    def __str__(self):
        return type(self).__name__
