import contextlib
from typing import ContextManager, Iterator

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.line_matcher.model_construction import model_iter_from_file_line_iter
from exactly_lib.impls.types.line_matcher.trace_rendering import LineMatcherLineRenderer
from exactly_lib.impls.types.matcher.impls import quantifier_matchers
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.logic_types import Quantifier


def sdv(quantifier: Quantifier, line_matcher_sdv: LineMatcherSdv) -> StringMatcherSdv:
    matcher = quantifier_matchers.sdv(
        ELEMENT_SETUP,
        quantifier,
        line_matcher_sdv,
    )
    return matcher


@contextlib.contextmanager
def _get_line_elements(tcds: TestCaseDs,
                       environment: ApplicationEnvironment,
                       string_matcher_model: StringSource
                       ) -> ContextManager[Iterator[LineMatcherLine]]:
    with string_matcher_model.contents().as_lines as lines:
        yield model_iter_from_file_line_iter(lines)


def _line_renderer(line: LineMatcherLine) -> DetailsRenderer:
    return LineMatcherLineRenderer(line)


ELEMENT_SETUP = quantifier_matchers.ElementSetup(
    quantifier_matchers.ElementRendering(
        matcher_options.LINE_ARGUMENT,
        syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT,
        _line_renderer,
    ),
    _get_line_elements,
)
