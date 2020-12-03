from typing import Sequence

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class StringSourceStructureBuilder:
    def __init__(self,
                 header: str,
                 details: Sequence[DetailsRenderer],
                 children: Sequence[StructureRenderer] = (),
                 ):
        self._header = header
        self._details = details
        self._children = children

    @staticmethod
    def of_details(header: str,
                   details: Sequence[DetailsRenderer],
                   ) -> 'StringSourceStructureBuilder':
        return StringSourceStructureBuilder(header, details, ())

    def build(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(self._header, None, self._details, self._children)

    def with_transformed_by(self, transformer: StructureRenderer) -> 'StringSourceStructureBuilder':
        transformation_renderer = renderers.NodeRendererFromParts(
            string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION,
            None,
            (),
            (transformer,),
        )
        return StringSourceStructureBuilder(
            self._header,
            self._details,
            tuple(self._children) + (transformation_renderer,),
        )
