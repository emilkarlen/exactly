from typing import Sequence

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.type_val_prims import string_transformer_descr
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class StringSourceStructureBuilder:
    def __init__(self,
                 header: str,
                 details: Sequence[DetailsRenderer],
                 children: Sequence[StructureRenderer] = (),
                 transformations: Sequence[StructureRenderer] = (),
                 ):
        self._header = header
        self._details = details
        self._children = children
        self._transformations = transformations

    @staticmethod
    def of_details(header: str,
                   details: Sequence[DetailsRenderer],
                   ) -> 'StringSourceStructureBuilder':
        return StringSourceStructureBuilder(header, details, ())

    def build(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self._header,
            None,
            self._details,
            tuple(self._children) + tuple(self._transformation_child()),
        )

    def with_transformed_by(self, transformer: StructureRenderer) -> 'StringSourceStructureBuilder':
        return StringSourceStructureBuilder(
            self._header,
            self._details,
            self._children,
            tuple(self._transformations) + (transformer,)
        )

    def _transformation_child(self) -> Sequence[StructureRenderer]:
        mb_transformer = string_transformer_descr.sequence_of_renderers__optional(self._transformations)
        if mb_transformer is None:
            return ()
        else:
            transformation_renderer = renderers.NodeRendererFromParts(
                string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION,
                None,
                (),
                (mb_transformer,),
            )
            return (transformation_renderer,)
