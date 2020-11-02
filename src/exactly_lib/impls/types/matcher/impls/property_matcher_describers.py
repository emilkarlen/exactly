from typing import Sequence, List

from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.matcher.property_matcher import PropertyMatcherDescriber
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matching_result import TraceRenderer, MatchingResult
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import NodeRenderer, NODE_DATA
from exactly_lib.util.description_tree.tree import Node


class IdenticalToMatcher(PropertyMatcherDescriber):
    def trace(self,
              matcher_result: MatchingResult,
              property_getter: StructureRenderer,
              ) -> TraceRenderer:
        return matcher_result.trace

    def structure(self,
                  matcher: StructureRenderer,
                  property_getter: StructureRenderer,
                  ) -> StructureRenderer:
        return matcher


class GetterWithMatcherAsChild(PropertyMatcherDescriber):
    def trace(self,
              matcher_result: MatchingResult,
              property_getter: StructureRenderer,
              ) -> TraceRenderer:
        class _Renderer(NodeRenderer[bool]):
            def render(self) -> Node[NODE_DATA]:
                getter = property_getter.render()
                matcher = matcher_result.trace.render()
                details = _details_list(getter.details)
                details += [custom_details.structure_tree_detail(c) for c in getter.children]
                return Node(
                    getter.header,
                    matcher_result.value,
                    details,
                    (matcher,),
                )

        return _Renderer()

    def structure(self,
                  matcher: StructureRenderer,
                  property_getter: StructureRenderer,
                  ) -> StructureRenderer:
        class _Renderer(NodeRenderer[bool]):
            def render(self) -> Node[NODE_DATA]:
                getter = property_getter.render()
                matcher_tree = matcher.render()
                details = list(getter.details)
                details += [tree.TreeDetail(c) for c in getter.children]
                return Node(
                    getter.header,
                    None,
                    details,
                    (matcher_tree,),
                )

        return _Renderer()


class GetterWithMatcherAsDetail(PropertyMatcherDescriber):
    def trace(self,
              matcher_result: MatchingResult,
              property_getter: StructureRenderer,
              ) -> TraceRenderer:
        class _Renderer(NodeRenderer[bool]):
            def render(self) -> Node[NODE_DATA]:
                getter = property_getter.render()
                matcher = matcher_result.trace.render()
                details = _details_list(getter.details)
                details += [custom_details.structure_tree_detail(c) for c in getter.children]
                details.append(tree.TreeDetail(matcher))
                return Node(
                    getter.header,
                    matcher_result.value,
                    details,
                    (),
                )

        return _Renderer()

    def structure(self,
                  matcher: StructureRenderer,
                  property_getter: StructureRenderer,
                  ) -> StructureRenderer:
        class _Renderer(NodeRenderer[bool]):
            def render(self) -> Node[NODE_DATA]:
                getter = property_getter.render()
                matcher_tree = matcher.render()
                details = list(getter.details)
                details += [tree.TreeDetail(c) for c in getter.children]
                details.append(tree.TreeDetail(matcher_tree))
                return Node(
                    getter.header,
                    None,
                    details,
                    (),
                )

        return _Renderer()


def _details_list(details: Sequence[tree.Detail]) -> List[tree.Detail]:
    return [
        _format_structure_detail(detail)
        for detail in details
    ]


def _format_structure_detail(detail: tree.Detail) -> tree.Detail:
    if isinstance(detail, tree.TreeDetail):
        return custom_details.structure_tree_detail(detail.tree)
    else:
        return detail
