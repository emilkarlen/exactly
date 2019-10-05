from exactly_lib.test_case_utils.file_matcher.impl.combinators import FileMatcherNot
from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


class FileMatcherImplBase(FileMatcher):
    def __init__(self):
        self._structure_renderer = renderers.CachedSingleInvokation(
            renderers.FromFunction(self._structure)
        )

    @property
    def negation(self) -> FileMatcher:
        return FileMatcherNot(self)

    @property
    def structure(self) -> NodeRenderer[None]:
        return self._structure_renderer

    def _structure(self) -> NodeRenderer[None]:
        return renderers.Constant(
            Node(self.name,
                 None,
                 (),
                 ()),
        )

    def _new_structure_builder(self) -> StructureBuilder:
        return StructureBuilder(self.name)
