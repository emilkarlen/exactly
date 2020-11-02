from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.type_val_prims.description.details_structured import WithDetailsDescription
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer

MODEL = TypeVar('MODEL')


class ModelConstructor(Generic[MODEL], WithDetailsDescription, ABC):
    @property
    def describer(self) -> DetailsRenderer:
        return details.empty()

    @abstractmethod
    def make_model(self, model: FileMatcherModel) -> MODEL:
        pass
