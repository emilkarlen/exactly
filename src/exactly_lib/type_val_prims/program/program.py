from typing import Sequence, Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import string_transformer, program
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.type_val_prims import string_transformer_descr
from exactly_lib.type_val_prims.description.structure_building import StructureBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer, WithNodeDescription
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.string_source import description as str_src_descr
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer


class Program(WithCachedNodeDescriptionBase):
    def __init__(self,
                 command: Command,
                 stdin: Sequence[StringSource],
                 transformation: Sequence[StringTransformer],
                 ):
        super().__init__()
        self._command = command
        self._stdin = stdin
        self._transformation = transformation
        if isinstance(transformation, StringTransformer):
            raise NotImplementedError('error terror')

    def _structure(self) -> StructureRenderer:
        return program_structure_renderer(self._command.new_structure_builder(),
                                          self._stdin,
                                          self._transformation)

    @property
    def command(self) -> Command:
        return self._command

    @property
    def stdin(self) -> Sequence[StringSource]:
        return self._stdin

    @property
    def transformation(self) -> Sequence[StringTransformer]:
        return self._transformation


_TRANSFORMER_NAME = ' '.join((string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION,
                              syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name))

_STDIN_NAME = ' '.join((program.STDIN_OPTION_STR,
                        syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.singular_name))


def program_structure_renderer(command: StructureBuilder,
                               stdin: Sequence[WithNodeDescription],
                               transformations: Sequence[WithNodeDescription],
                               ) -> NodeRenderer[None]:
    mb_stdin_node = stdin_node_renderer(stdin)
    if mb_stdin_node:
        command.append_child(mb_stdin_node)
    mb_transformation_node = _transformation_node(transformations)
    if mb_transformation_node:
        command.append_child(mb_transformation_node)

    return command.as_render()


def _transformation_node(transformations: Sequence[WithNodeDescription]) -> Optional[StructureRenderer]:
    if not transformations:
        return None
    else:
        transformer = string_transformer_descr.sequence_of_unknown_num_operands(transformations)
        return renderers.NodeRendererFromParts(
            _TRANSFORMER_NAME,
            None,
            (),
            (transformer,),
        )


def stdin_node_renderer(string_sources: Sequence[WithNodeDescription]) -> Optional[StructureRenderer]:
    if not string_sources:
        return None
    else:
        string_source = str_src_descr.sequence_of_unknown_num_operands(string_sources)
        return renderers.NodeRendererFromParts(
            _STDIN_NAME,
            None,
            (),
            (string_source,),
        )


def command_w_stdin_renderer(command: StructureBuilder,
                             stdin: Sequence[WithNodeDescription],
                             ) -> StructureRenderer:
    mb_stdin = stdin_node_renderer(stdin)
    if mb_stdin:
        command.append_child(mb_stdin)

    return command.build()
