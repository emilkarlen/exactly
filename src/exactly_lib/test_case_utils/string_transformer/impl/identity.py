from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel
from exactly_lib.util.description_tree import renderers


class IdentityStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformer):
    _NAME = 'identity'

    @property
    def name(self) -> str:
        return 'identity'

    @property
    def is_identity_transformer(self) -> bool:
        return True

    def _structure(self) -> StructureRenderer:
        return renderers.header_only(self._NAME)

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return lines
