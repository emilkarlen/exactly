from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.program.stdin import StdinData
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


class Program(WithCachedTreeStructureDescriptionBase):
    def __init__(self,
                 command: Command,
                 stdin: StdinData,
                 transformation: StringTransformer,
                 ):
        super().__init__()
        self._command = command
        self._stdin = stdin
        self._transformation = transformation

    def _structure(self) -> StructureRenderer:
        return _StructureRendererOfPrimitive(self._command,
                                             self._transformation)

    @property
    def command(self) -> Command:
        return self._command

    @property
    def stdin(self) -> StdinData:
        return self._stdin

    @property
    def transformation(self) -> StringTransformer:
        return self._transformation


NAME = ' '.join((string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION,
                 syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name))


class _StructureRendererOfPrimitive(NodeRenderer[None]):

    def __init__(self,
                 command: Command,
                 transformation: StringTransformer,
                 ):
        self._command = command
        self._transformation = transformation

    def render(self) -> Node[None]:
        ret_val = self._command.structure()
        if not self._transformation.is_identity_transformer:
            ret_val.append_child(self._transformation_node())

        return ret_val.as_render().render()

    def _transformation_node(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            NAME,
            None,
            (),
            (self._transformation.structure(),),
        )
