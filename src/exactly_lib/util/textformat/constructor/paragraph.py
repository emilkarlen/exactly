from typing import List

from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.structure.core import ParagraphItem


class ParagraphItemsConstructor:
    def apply(self, environment: ConstructionEnvironment) -> List[ParagraphItem]:
        raise NotImplementedError('abstract method')
