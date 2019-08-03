from typing import Sequence, Any

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case_utils.err_msg2.env_dep_text import RendererResolver, TextResolver
from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


def of_old(resolver: ErrorMessageResolver) -> RendererResolver[Sequence[MajorBlock]]:
    return _ResolverFromOldResolver(resolver)


def constant(x: Any,
             is_line_ended: bool = False) -> TextResolver:
    return _ConstantPreFormatted(x, is_line_ended)


class _ResolverFromOldResolver(RendererResolver[Sequence[MajorBlock]]):
    def __init__(self, old: ErrorMessageResolver):
        self._old = old

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[Sequence[MajorBlock]]:
        return text_docs.single_pre_formatted_line_object(self._old.resolve(environment),
                                                          True)


class _ConstantPreFormatted(RendererResolver[Sequence[MajorBlock]]):
    def __init__(self,
                 x: Any,
                 is_line_ended: bool = False
                 ):
        self._x = x
        self._is_line_ended = is_line_ended

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[Sequence[MajorBlock]]:
        return text_docs.single_pre_formatted_line_object(self._x,
                                                          self._is_line_ended)
