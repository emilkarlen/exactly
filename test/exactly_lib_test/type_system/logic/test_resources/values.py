from typing import Iterable, Callable

from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderers import Constant
from exactly_lib_test.test_case_utils.matcher.test_resources.matchers import MatcherTestImplBase
from exactly_lib_test.type_system.logic.string_transformer.test_resources import StringTransformerTestImplBase
from exactly_lib_test.util.render.test_resources import renderers
from exactly_lib_test.util.render.test_resources import renderers as renderers_tr


class FakeStringTransformer(StringTransformerTestImplBase):
    def structure(self) -> StructureRenderer:
        return renderers_tr.structure_renderer_for_arbitrary_object(self)

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError('should never be used')


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

    @property
    def negation(self) -> MatcherWTraceAndNegation[LineMatcherLine]:
        return LineMatcherFromPredicates(
            self.line_num,
            self.line_contents,
            not self._is_negated,
        )

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
