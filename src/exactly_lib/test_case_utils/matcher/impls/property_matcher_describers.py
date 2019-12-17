from exactly_lib.test_case_utils.matcher.property_matcher import PropertyMatcherDescriber
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, TraceRenderer
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
                details = list(getter.details)
                details += [tree.TreeDetail(c) for c in getter.children]
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
                details = list(getter.details)
                details += [tree.TreeDetail(c) for c in getter.children]
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
