from typing import Any

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg2.env_dep_text import TextResolver, SequenceRendererResolver
from exactly_lib.type_system.err_msg.error_message import ErrorMessageResolver
from exactly_lib.util.simple_textstruct.structure import MajorBlock


def of_old(resolver: ErrorMessageResolver) -> TextResolver:
    return _ResolverFromOldResolver(resolver)


def as_old(resolver: TextResolver) -> ErrorMessageResolver:
    return _ResolverAsOldResolver(resolver)


def constant_renderer(renderer: TextRenderer) -> TextResolver:
    return _OfConstantRenderer(renderer)


def constant(x: Any,
             is_line_ended: bool = False) -> TextResolver:
    return _ConstantPreFormatted(x, is_line_ended)


class _OfConstantRenderer(SequenceRendererResolver[MajorBlock]):
    def __init__(self, renderer: TextRenderer):
        self._renderer = renderer

    def resolve_sequence(self) -> TextRenderer:
        return self._renderer


class _ResolverAsOldResolver(ErrorMessageResolver):
    def __init__(self, resolver: TextResolver):
        self._resolver = resolver

    def resolve(self) -> str:
        return print.print_to_str(self._resolver.resolve_sequence().render_sequence())


class _ResolverFromOldResolver(SequenceRendererResolver[MajorBlock]):
    def __init__(self, old: ErrorMessageResolver):
        self._old = old

    def resolve_sequence(self) -> TextRenderer:
        return self._old.resolve__tr()


class _ConstantPreFormatted(SequenceRendererResolver[MajorBlock]):
    def __init__(self,
                 x: Any,
                 is_line_ended: bool = False
                 ):
        self._x = x
        self._is_line_ended = is_line_ended

    def resolve_sequence(self) -> TextRenderer:
        return text_docs.single_pre_formatted_line_object(self._x,
                                                          self._is_line_ended)
