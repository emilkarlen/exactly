from abc import ABC

from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherAdv
from exactly_lib.util.description_tree import renderers


class FilesMatcherImplBase(MatcherImplBase[FilesMatcherModel], ABC):
    pass


class FilesMatcherDdvImplBase(MatcherDdv[FilesMatcherModel], ABC):
    def structure(self) -> StructureRenderer:
        """
        The structure of the object, that can be used in traced.

        The returned tree is constant.
        """
        return renderers.NodeRendererFromParts(
            'TODO files-matcher name',
            None,
            (),
            (),
        )


class FilesMatcherAdvImplBase(MatcherAdv[FilesMatcherModel], ABC):
    pass
