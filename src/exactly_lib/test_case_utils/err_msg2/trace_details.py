from typing import Sequence, Iterable

from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive, PathDescriberForValue
from exactly_lib.type_system.trace import trace
from exactly_lib.type_system.trace.trace import DetailVisitor, Detail, PreFormattedStringDetail, StringDetail
from exactly_lib.type_system.trace.trace_renderer import DetailsRenderer
from exactly_lib.util import strings
from exactly_lib.util.strings import ToStringObject

_EXPECTED = 'Expected'
_ACTUAL = 'Actual'


class PathValueDetailsRenderer(DetailsRenderer):
    def __init__(self, path: PathDescriberForValue):
        self._path = path

    def render(self) -> Sequence[Detail]:
        return [
            trace.StringDetail(self._path.value.render()),
        ]


class PathValueAndPrimitiveDetailsRenderer(DetailsRenderer):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def render(self) -> Sequence[Detail]:
        return [
            trace.StringDetail(self._path.value.render()),
            trace.StringDetail(self._path.primitive.render()),
        ]


class DetailsRendererOfConstant(DetailsRenderer):
    def __init__(self, detail: Detail):
        self._detail = detail

    def render(self) -> Sequence[Detail]:
        return [self._detail]


class ConstantString(DetailsRenderer):
    def __init__(self, to_string_object: ToStringObject):
        self._to_string_object = to_string_object

    def render(self) -> Sequence[Detail]:
        return [trace.StringDetail(self._to_string_object)]


class HeaderAndValue(DetailsRenderer):
    def __init__(self,
                 header: ToStringObject,
                 value: DetailsRenderer,
                 ):
        self._header = header
        self._value = value

    def render(self) -> Sequence[Detail]:
        ret_val = [trace.StringDetail(self._header)]

        ret_val += Indented(self._value).render()

        return ret_val


class Expected(DetailsRenderer):
    def __init__(self, expected: DetailsRenderer):
        self._expected = expected

    def render(self) -> Sequence[Detail]:
        ret_val = [trace.StringDetail(_EXPECTED)]

        ret_val += Indented(self._expected).render()

        return ret_val


class Actual(DetailsRenderer):
    def __init__(self, actual: DetailsRenderer):
        self._actual = actual

    def render(self) -> Sequence[Detail]:
        ret_val = [trace.StringDetail(_ACTUAL)]

        ret_val += Indented(self._actual).render()

        return ret_val


class Indented(DetailsRenderer, DetailVisitor[Detail]):
    INDENT = '  '

    def __init__(self, details: DetailsRenderer):
        self._details = details

    def render(self) -> Sequence[Detail]:
        return [
            detail.accept(self)
            for detail in self._details.render()
        ]

    def visit_string(self, x: StringDetail) -> Detail:
        return StringDetail(strings.Concatenate((self.INDENT, x.string)))

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> Detail:
        return x


class StringList(DetailsRenderer):
    def __init__(self, items: Iterable[ToStringObject]):
        self._items = items

    def render(self) -> Sequence[Detail]:
        return [
            trace.StringDetail(item)
            for item in self._items
        ]
