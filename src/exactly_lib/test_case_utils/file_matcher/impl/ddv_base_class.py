from abc import ABC

from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.util.description_tree import renderers, tree


class FileMatcherDdvImplBase(MatcherDdv[FileMatcherModel], ABC):
    def structure(self) -> StructureRenderer:
        return renderers.Constant(
            tree.Node('file-matcher TODO', None, (), ())
        )
