from abc import ABC
from typing import Generic

from exactly_lib.impls.description_tree.tree_structured import WithCachedNameAndNodeStructureDescriptionBase
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, MatcherWTrace


class MatcherImplBase(Generic[MODEL],
                      MatcherWTrace[MODEL],
                      WithCachedNameAndNodeStructureDescriptionBase,
                      ABC):
    def __init__(self):
        WithCachedNameAndNodeStructureDescriptionBase.__init__(self)

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)
