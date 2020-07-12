import re
from typing import Sequence, Iterable, Pattern, Match, Any, TypeVar, Generic, Callable

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering.description_tree import layout__detail
from exactly_lib.common.report_rendering.description_tree import layout__node_wo_data
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.err_msg import path_rendering
from exactly_lib.type_system.data import string_or_path_ddvs
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive, PathDescriberForDdv
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription, StructureRenderer
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import tree, details
from exactly_lib.util.description_tree.details import HeaderAndValue
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.str_.str_constructor import ToStringObject

HAS_MORE_DATA_MARKER = '...'

_EXPECTED = 'Expected'
_ACTUAL = 'Actual'
_MATCH = 'Match'

_RHS = 'RHS'
_ACTUAL_LHS = 'Actual LHS'

_REGEX_FULL_MATCH = 'Full match'
_REGEX_CONTAINS = 'Contains'
_REGEX_IGNORE_CASE = 'Case insensitive'


def expected(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_EXPECTED, value,
                          layout__detail.STANDARD_HEADER_TEXT_STYLE)


def rhs(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_RHS, value)


def actual(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_ACTUAL, value,
                          layout__detail.STANDARD_HEADER_TEXT_STYLE)


def actual__custom(header: ToStringObject, value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(header, value,
                          layout__detail.STANDARD_HEADER_TEXT_STYLE)


def actual_lhs(value: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_ACTUAL_LHS, value,
                          layout__detail.STANDARD_HEADER_TEXT_STYLE)


def match(matching_object: DetailsRenderer) -> DetailsRenderer:
    return HeaderAndValue(_MATCH, matching_object,
                          layout__detail.STANDARD_HEADER_TEXT_STYLE)


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


E = TypeVar('E')


class ElementList(Generic[E], DetailsRenderer):
    def __init__(self,
                 element_renderer: Callable[[E], Detail],
                 elements: Iterable[E],
                 ):
        self._element_renderer = element_renderer
        self._elements = elements

    def render(self) -> Sequence[Detail]:
        return [
            self._element_renderer(element)
            for element in self._elements
        ]


def string_list(items: Iterable[ToStringObject]) -> DetailsRenderer:
    return ElementList(
        _render_string,
        items,
    )


def _render_string(x: ToStringObject) -> Detail:
    return tree.StringDetail(x)


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
    def __init__(self, pattern: Pattern[str]):
        self._pattern = pattern

    def render(self) -> Sequence[Detail]:
        pattern_string = details.String(self._pattern.pattern)
        renderer = regex(bool(self._pattern.flags & re.IGNORECASE), pattern_string)
        return renderer.render()


class OptionRenderer(DetailsRenderer):
    def __init__(self, option: a.OptionName):
        self._option = option

    def render(self) -> Sequence[Detail]:
        renderer = details.String(option_syntax.option_syntax(self._option))
        return renderer.render()


def optional_option(option: a.OptionName,
                    has_option: bool) -> DetailsRenderer:
    return (
        OptionRenderer(option)
        if has_option
        else
        details.empty()
    )


class PatternMatchRenderer(DetailsRenderer):
    def __init__(self, match: Match):
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
            sr = sr + HAS_MORE_DATA_MARKER
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


class TreeStructure(DetailsRenderer):
    def __init__(self, tree_structure: StructureRenderer):
        self._tree_structure = tree_structure

    def render(self) -> Sequence[Detail]:
        return [structure_tree_detail(self._tree_structure.render())]


class WithTreeStructure(DetailsRenderer):
    def __init__(self, tree_structured: WithTreeStructureDescription):
        self._tree_structured = tree_structured

    def render(self) -> Sequence[Detail]:
        return [structure_tree_detail(self._tree_structured.structure().render())]


def structure_tree_detail(structure_tree: tree.Node[Any]) -> tree.Detail:
    return tree.TreeDetail(structure_tree,
                           layout__node_wo_data.STRUCTURE_NODE_HEADER_TEXT_STYLE)


class ExpectedAndActual(DetailsRenderer):
    def __init__(self,
                 expected: DetailsRenderer,
                 actual: DetailsRenderer,
                 initial_explanation: DetailsRenderer = details.DetailsRendererOfConstant(()),
                 ):
        self._expected = expected
        self._actual = actual
        self._initial_explanation = initial_explanation

    def render(self) -> Sequence[Detail]:
        ret_val = []
        ret_val += list(self._initial_explanation.render())
        ret_val += list(expected(self._expected).render())
        ret_val += list(actual(self._actual).render())

        return ret_val
