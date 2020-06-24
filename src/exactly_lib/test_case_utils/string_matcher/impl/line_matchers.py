import contextlib
from typing import ContextManager, Iterator

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.line_matcher.model_construction import model_iter_from_file_line_iter
from exactly_lib.test_case_utils.line_matcher.trace_rendering import LineMatcherLineRenderer
from exactly_lib.test_case_utils.matcher.impls import quantifier_matchers
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine, LineMatcherSdv
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcherSdv
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
def _get_line_elements(tcds: Tcds,
                       environment: ApplicationEnvironment,
                       string_matcher_model: FileToCheck
                       ) -> ContextManager[Iterator[LineMatcherLine]]:
    with string_matcher_model.lines() as lines:
        yield model_iter_from_file_line_iter(iter(lines))


def _line_renderer(line: LineMatcherLine) -> DetailsRenderer:
    return LineMatcherLineRenderer(line)


ELEMENT_SETUP = quantifier_matchers.ElementSetup(
    quantifier_matchers.ElementRendering(
        matcher_options.LINE_ARGUMENT,
        syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.singular_name,
        _line_renderer,
    ),
    _get_line_elements,
)
