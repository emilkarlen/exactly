from typing import Sequence, Iterable, Pattern, Match

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_utils.err_msg2 import path_rendering
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.type_system.data import string_or_file_ref_values
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive, PathDescriberForValue
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.strings import ToStringObject

_EXPECTED = 'Expected'
_ACTUAL = 'Actual'
_MATCH = 'Match'


class DetailsRendererOfConstant(DetailsRenderer):
    def __init__(self, detail: Detail):
        self._detail = detail

    def render(self) -> Sequence[Detail]:
        return [self._detail]


class String(DetailsRenderer):
    def __init__(self, to_string_object: ToStringObject):
        self._to_string_object = to_string_object

    def render(self) -> Sequence[Detail]:
        return [tree.StringDetail(self._to_string_object)]


class PreFormattedString(DetailsRenderer):
    def __init__(self,
                 to_string_object: ToStringObject,
                 string_is_line_ended: bool = False,
                 ):
        self._to_string_object = to_string_object
        self._string_is_line_ended = string_is_line_ended

    def render(self) -> Sequence[Detail]:
        return [tree.PreFormattedStringDetail(self._to_string_object,
                                              self._string_is_line_ended)]


class HeaderAndValue(DetailsRenderer):
    def __init__(self,
                 header: ToStringObject,
                 value: DetailsRenderer,
                 ):
        self._header = header
        self._value = value

    def render(self) -> Sequence[Detail]:
        return [
            tree.HeaderAndValueDetail(
                self._header,
                self._value.render()
            )
        ]


def expected(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_EXPECTED, value)


def actual(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_ACTUAL, value)


def match(matching_object: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_MATCH, matching_object)


class PathValueDetailsRenderer(DetailsRenderer):
    def __init__(self, path: PathDescriberForValue):
        self._path = path

    def render(self) -> Sequence[Detail]:
        return [
            tree.StringDetail(self._path.value.render()),
        ]


class PathValueAndPrimitiveDetailsRenderer(DetailsRenderer):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def render(self) -> Sequence[Detail]:
        return [
            tree.StringDetail(self._path.value.render()),
            tree.StringDetail(self._path.primitive.render()),
        ]


class PathPrimitiveDetailsRenderer(DetailsRenderer):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def render(self) -> Sequence[Detail]:
        renderer = path_rendering.PathRepresentationsRenderersForPrimitive(self._path)
        return [
            tree.StringDetail(renderer.render())
            for renderer in renderer.renders()
        ]


class StringList(DetailsRenderer):
    def __init__(self, items: Iterable[ToStringObject]):
        self._items = items

    def render(self) -> Sequence[Detail]:
        return [
            tree.StringDetail(item)
            for item in self._items
        ]


class StringOrPath(DetailsRenderer):
    def __init__(self,
                 string_or_path: string_or_file_ref_values.StringOrPath,
                 ):
        self._string_or_path = string_or_path

    def render(self) -> Sequence[Detail]:
        return self._renderer().render()

    def _renderer(self) -> DetailsRenderer:
        x = self._string_or_path
        if x.is_path:
            return HeaderAndValue(
                syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
                PathPrimitiveDetailsRenderer(
                    x.file_ref_value.describer
                )
            )
        else:
            return HeaderAndValue(
                syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
                StringAsSingleLineWithMaxLenDetailsRenderer(x.string_value)
            )


class PatternRenderer(DetailsRenderer):
    def __init__(self,
                 is_full_match: bool,
                 pattern: Pattern[str],
                 ):
        self._pattern = pattern
        self._is_full_match = is_full_match

    def render(self) -> Sequence[Detail]:
        s = self._pattern.pattern
        if self._is_full_match:
            s += option_syntax.option_syntax(matcher_options.FULL_MATCH_ARGUMENT_OPTION)

        return [
            tree.StringDetail(s)
        ]


class PatternMatchRenderer(DetailsRenderer):
    def __init__(self,
                 match: Match,
                 ):
        self._match = match

    def render(self) -> Sequence[Detail]:
        return StringAsSingleLineWithMaxLenDetailsRenderer(self._match.group()).render()


class OfTextRenderer(DetailsRenderer):
    def __init__(self, text: TextRenderer):
        self._text = text

    def render(self) -> Sequence[Detail]:
        return [
            tree.PreFormattedStringDetail(
                print.print_to_str(self._text.render_sequence())
            )
        ]


class StringAsSingleLineWithMaxLenDetailsRenderer(DetailsRenderer):
    def __init__(self, value: str, max_chars_to_print: int = 100):
        self._value = value
        self._max_chars_to_print = max_chars_to_print

    def render(self) -> Sequence[Detail]:
        s = self._value
        s = s[:self._max_chars_to_print]
        sr = repr(s)
        if len(s) != len(self._value):
            sr = sr + '...'
        return [
            tree.StringDetail(sr)
        ]
