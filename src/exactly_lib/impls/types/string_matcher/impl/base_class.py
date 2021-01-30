from abc import ABC

from exactly_lib.impls.description_tree.tree_structured import WithCachedNameAndNodeStructureDescriptionBase
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class StringMatcherImplBase(WithCachedNameAndNodeStructureDescriptionBase,
                            MatcherWTrace[StringSource],
                            ABC):

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)


class StringMatcherDdvImplBase(MatcherDdv[StringSource], ABC):
    pass


class StringMatcherAdvImplBase(MatcherAdv[StringSource], ABC):
    pass
