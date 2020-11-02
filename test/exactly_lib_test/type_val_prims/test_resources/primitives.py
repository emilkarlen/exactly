from typing import Callable

from exactly_lib.impls.types.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderers import Constant
from exactly_lib_test.impls.types.matcher.test_resources.matchers import MatcherTestImplBase
from exactly_lib_test.util.render.test_resources import renderers


class FileMatcherTestImpl(MatcherImplBase[FileMatcherModel]):
    @property
    def name(self) -> str:
        return str(type(self))

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        raise NotImplementedError('should never be used')


def is_identical_to(line_num: int, line_contents: str) -> LineMatcher:
    return line_matcher_from_predicates(lambda x: x == line_num,
                                        lambda x: x == line_contents)


class LineMatcherFromPredicates(MatcherTestImplBase[LineMatcherLine]):
    def __init__(self,
                 line_num_predicate: Callable[[int], bool] = lambda x: True,
                 line_contents_predicate: Callable[[str], bool] = lambda x: True,
                 is_negated: bool = False):
        super().__init__()
        self.line_num = line_num_predicate
        self.line_contents = line_contents_predicate
        self._is_negated = is_negated

    @property
    def name(self) -> str:
        return str(type(self))

    def _structure(self) -> StructureRenderer:
        return renderers.structure_renderer_for_arbitrary_object(self)

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        result = self._matches(line)
        return MatchingResult(
            result,
            Constant(tree.Node(self.name,
                               result,
                               (),
                               ()))
        )

    def _matches(self, line: LineMatcherLine) -> bool:
        positive_result = self.line_num(line[0]) and self.line_contents(line[1])
        return (
            not positive_result
            if self._is_negated
            else
            positive_result
        )


def line_matcher_from_predicates(line_num_predicate: Callable[[int], bool] = lambda x: True,
                                 line_contents_predicate: Callable[[str], bool] = lambda x: True) -> LineMatcher:
    return LineMatcherFromPredicates(line_num_predicate,
                                     line_contents_predicate)
