from abc import ABC

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.string_model import StringModel


class StringMatcherImplBase(WithCachedNameAndTreeStructureDescriptionBase,
                            MatcherWTrace[StringModel],
                            ABC):

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)


class StringMatcherDdvImplBase(MatcherDdv[StringModel], ABC):
    pass


class StringMatcherAdvImplBase(MatcherAdv[StringModel], ABC):
    pass
