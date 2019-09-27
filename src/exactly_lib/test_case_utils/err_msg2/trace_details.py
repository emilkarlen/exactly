from typing import Any

from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib.type_system.trace import trace
from exactly_lib.type_system.trace.impls.trace_building import TraceBuilder
from exactly_lib.type_system.trace.trace import DetailVisitor, Detail, PreFormattedStringDetail, StringDetail
from exactly_lib.type_system.trace.trace_renderer import DetailRenderer

_EXPECTED = 'Expected'
_ACTUAL = 'Actual'


class PathDetailRenderer(DetailRenderer):
    def __init__(self, path: DescribedPathPrimitive):
        self._path = path

    def render(self) -> Detail:
        return trace.StringDetail(self._path.describer.value.render())


class PathValueAndPrimitiveDetailRenderer(DetailRenderer):
    def __init__(self, path: DescribedPathPrimitive):
        self._path = path

    def render(self) -> Detail:
        return trace.StringDetail(self._path.describer.value.render())


class DetailRendererOfConstant(DetailRenderer):
    def __init__(self, detail: Detail):
        self._detail = detail

    def render(self) -> Detail:
        return self._detail


def constant_to_string_object(to_string_object: Any) -> DetailRenderer:
    return DetailRendererOfConstant(trace.StringDetail(str(to_string_object)))


_EXPECTED_HEADER_RENDERER = constant_to_string_object(_EXPECTED)
_ACTUAL_HEADER_RENDERER = constant_to_string_object(_ACTUAL)


def append_header_and_value_details(tb: TraceBuilder,
                                    header: DetailRenderer,
                                    value: DetailRenderer) -> TraceBuilder:
    tb.append_detail(header)
    tb.append_detail(_IndentRenderer(value))
    return tb


def append_detail_for_expected(tb: TraceBuilder,
                               expected: DetailRenderer) -> TraceBuilder:
    return append_header_and_value_details(tb, _EXPECTED_HEADER_RENDERER, expected)


def append_detail_for_actual(tb: TraceBuilder,
                             actual: DetailRenderer) -> TraceBuilder:
    return append_header_and_value_details(tb, _ACTUAL_HEADER_RENDERER, actual)


def append_header_and_path(tb: TraceBuilder,
                           header: DetailRenderer,
                           path: DescribedPathPrimitive) -> TraceBuilder:
    return append_header_and_value_details(
        tb,
        header,
        PathDetailRenderer(path),
    )


class _IndentRenderer(DetailRenderer, DetailVisitor[Detail]):
    # TODO Remove this when Detail structure supports indentation.

    INDENT = '  '

    def __init__(self, detail: DetailRenderer):
        self._detail = detail

    def render(self) -> Detail:
        return self._detail.render().accept(self)

    def visit_string(self, x: StringDetail) -> Detail:
        return StringDetail(self.INDENT + x.string)

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> Detail:
        return x
