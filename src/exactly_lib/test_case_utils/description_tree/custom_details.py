import re
from typing import Sequence, Iterable, Pattern, Match

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.err_msg import path_rendering
from exactly_lib.type_system.data import string_or_path_ddvs
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive, PathDescriberForDdv
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.util.description_tree import tree, details
from exactly_lib.util.description_tree.details import HeaderAndValue
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.strings import ToStringObject

_EXPECTED = 'Expected'
_ACTUAL = 'Actual'
_MATCH = 'Match'

_RHS = 'RHS'
_ACTUAL_LHS = 'Actual LHS'

_REGEX_FULL_MATCH = 'Full match'
_REGEX_CONTAINS = 'Contains'
_REGEX_IGNORE_CASE = 'Case insensitive'


def expected(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_EXPECTED, value)


def rhs(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_RHS, value)


def actual(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_ACTUAL, value)


def actual_lhs(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_ACTUAL_LHS, value)


def match(matching_object: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_MATCH, matching_object)


class PathDdvDetailsRenderer(DetailsRenderer):
    def __init__(self, path: PathDescriberForDdv):
        self._path = path

    def render(self) -> Sequence[Detail]:
        return [
            tree.StringDetail(self._path.value.render()),
        ]


class PathDdvAndPrimitiveDetailsRenderer(DetailsRenderer):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def render(self) -> Sequence[Detail]:
        return [
            tree.StringDetail(self._path.value.render()),
            tree.StringDetail(self._path.primitive.render()),
        ]


class PathDdvAndPrimitiveIfRelHomeAsIndentedDetailsRenderer(DetailsRenderer):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def render(self) -> Sequence[Detail]:
        ret_val = [tree.StringDetail(self._path.value.render())]
        if self._path.resolving_dependency is DirectoryStructurePartition.HDS:
            ret_val.append(tree.IndentedDetail((tree.StringDetail(self._path.primitive.render()),)))

        return ret_val


def path_primitive_details_renderer(path: PathDescriberForPrimitive) -> DetailsRenderer:
    """Renders DDV, and optional primitive if is rel HDS"""
    return PathDetailsRenderer(path_rendering.PathRepresentationsRenderersForPrimitive(path))


class PathDetailsRenderer(DetailsRenderer):
    def __init__(self, renderer: path_rendering.PathRepresentationsRenderers):
        self._renderer = renderer

    def render(self) -> Sequence[Detail]:
        return [
            tree.StringDetail(renderer.render())
            for renderer in self._renderer.renders()
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
                 string_or_path: string_or_path_ddvs.StringOrPath,
                 ):
        self._string_or_path = string_or_path

    def render(self) -> Sequence[Detail]:
        return self._renderer().render()

    def _renderer(self) -> DetailsRenderer:
        x = self._string_or_path
        if x.is_path:
            return HeaderAndValue(
                syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
                path_primitive_details_renderer(x.path_value.describer)
            )
        else:
            return HeaderAndValue(
                syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
                StringAsSingleLineWithMaxLenDetailsRenderer(x.string_value)
            )


class StringOrPathDdv(DetailsRenderer):
    def __init__(self,
                 string_or_path: string_or_path_ddvs.StringOrPathDdv,
                 ):
        self._string_or_path = string_or_path

    def render(self) -> Sequence[Detail]:
        return self._renderer().render()

    def _renderer(self) -> DetailsRenderer:
        x = self._string_or_path
        if x.is_path:
            return HeaderAndValue(
                syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
                PathDdvDetailsRenderer(x.path.describer())
            )
        else:
            return HeaderAndValue(
                syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
                StringAsSingleLineWithMaxLenDetailsRenderer(x.string.describer().render())
            )


def regex_with_config_renderer(is_full_match: bool,
                               pattern: DetailsRenderer,
                               ) -> DetailsRenderer:
    header = (
        _REGEX_FULL_MATCH
        if is_full_match
        else
        _REGEX_CONTAINS
    )
    return HeaderAndValue(
        header,
        pattern,
    )


def regex(ignore_case: bool, pattern: DetailsRenderer) -> DetailsRenderer:
    return (
        HeaderAndValue(_REGEX_IGNORE_CASE, pattern)
        if ignore_case
        else
        pattern
    )


class PatternRenderer(DetailsRenderer):
    def __init__(self,
                 pattern: Pattern[str],
                 ):
        self._pattern = pattern

    def render(self) -> Sequence[Detail]:
        pattern_string = details.String(self._pattern.pattern)
        renderer = regex(self._pattern.flags & re.IGNORECASE, pattern_string)
        return renderer.render()


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


class ComparatorExpression(DetailsRenderer):
    def __init__(self,
                 comparator: comparators.ComparisonOperator,
                 rhs: Renderer[str],
                 ):
        self._comparator = comparator
        self._rhs = rhs

    def render(self) -> Sequence[Detail]:
        return [
            tree.StringDetail(' '.join([
                self._comparator.name,
                self._rhs.render(),
            ]))
        ]


class WithTreeStructure(DetailsRenderer):
    def __init__(self, tree_structured: WithTreeStructureDescription):
        self._tree_structured = tree_structured

    def render(self) -> Sequence[Detail]:
        return [tree.TreeDetail(self._tree_structured.structure().render())]


class ExpectedAndActual(DetailsRenderer):
    def __init__(self,
                 expected: DetailsRenderer,
                 actual: DetailsRenderer,
                 ):
        self._expected = expected
        self._actual = actual

    def render(self) -> Sequence[Detail]:
        ret_val = expected(self._expected).render()
        ret_val += actual(self._actual).render()

        return ret_val
