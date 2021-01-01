from abc import ABC
from typing import Generic, Callable
from typing import TypeVar, List

from exactly_lib.definitions import logic
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace, MatcherStdTypeVisitor
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.util.render.test_resources import renderers as renderers_tr

MODEL = TypeVar('MODEL')
ACTUAL = TypeVar('ACTUAL')

T = TypeVar('T')

STRUCTURE_FOR_TEST = renderers.header_only('test-resource-structure')


class MatcherTestImplBase(Generic[MODEL],
                          MatcherWTrace[MODEL],
                          ABC):

    @property
    def name(self) -> str:
        return str(type(self))

    def structure(self) -> StructureRenderer:
        return renderers_tr.structure_renderer_for_arbitrary_object(self)


class ConstantMatcherTestImplBase(Generic[MODEL], MatcherWTrace[MODEL], ABC):
    def __init__(self, result: bool):
        self._result = result

    def accept(self, visitor: MatcherStdTypeVisitor[MODEL, T]) -> T:
        return visitor.visit_constant(self._result)


class ConstantMatcherWithCustomName(Generic[MODEL], ConstantMatcherTestImplBase[MODEL]):
    def __init__(self,
                 name: str,
                 result: bool,
                 ):
        super().__init__(result)
        self._name = name

        self._trace_tree = tree.Node(name,
                                     result,
                                     (tree.StringDetail(logic.BOOLEANS[result]),),
                                     ())
        self._matching_result = MatchingResult(
            result,
            renderers.Constant(
                self._trace_tree
            ),
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def trace_tree(self) -> tree.Node[bool]:
        return self._trace_tree

    def structure(self) -> StructureRenderer:
        return renderers.header_only(self._name)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        return self._matching_result


class ConstantMatcherWithCustomTrace(Generic[MODEL], ConstantMatcherTestImplBase[MODEL]):
    def __init__(self,
                 mk_trace: Callable[[T], tree.Node[T]],
                 result: bool,
                 ):
        super().__init__(result)
        self._mk_trace = mk_trace

        self._matching_result = MatchingResult(
            result,
            renderers.Constant(mk_trace(result)),
        )

    @property
    def name(self) -> str:
        raise NotImplementedError('name: unsupported')

    def structure(self) -> StructureRenderer:
        return renderers.Constant(self._mk_trace(None))

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        return self._matching_result


class MatcherThatRegistersModelArgument(Generic[MODEL], MatcherTestImplBase[MODEL]):
    def __init__(self,
                 registry: List[MODEL],
                 constant_result: bool):
        self._registry = registry
        self._constant_result = constant_result

    @property
    def name(self) -> str:
        return str(type(self))

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        self._registry.append(model)
        return MatchingResult(self._constant_result,
                              renderers.Constant(tree.Node(self.name,
                                                           self._constant_result,
                                                           (),
                                                           ())))


class MatcherThatReportsHardError(Generic[MODEL], MatcherTestImplBase[MODEL]):
    def __init__(self, error_message: str = 'unconditional hard error'):
        super().__init__()
        self.error_message = error_message

    @property
    def name(self) -> str:
        return str(type(self))

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        raise HardErrorException(new_single_string_text_for_test(self.error_message))
