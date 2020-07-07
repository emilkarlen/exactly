from abc import ABC

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherAdv, \
    MatcherWTrace
from exactly_lib.type_system.logic.string_model import StringModel


class StringMatcherImplBase(WithCachedNameAndTreeStructureDescriptionBase,
                            MatcherWTrace[StringModel],
                            ABC):

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)


class StringMatcherDdvImplBase(MatcherDdv[StringModel], ABC):
    pass


class StringMatcherAdvImplBase(MatcherAdv[StringModel], ABC):
    pass
