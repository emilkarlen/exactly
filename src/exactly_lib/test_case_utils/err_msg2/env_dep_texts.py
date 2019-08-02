from typing import Sequence

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case_utils.err_msg2.env_dep_text import TextResolver
from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


def of_old(resolver: ErrorMessageResolver) -> TextResolver[Sequence[MajorBlock]]:
    return _TextResolverFromOldResolver(resolver)


class _TextResolverFromOldResolver(TextResolver[Sequence[MajorBlock]]):
    def __init__(self, old: ErrorMessageResolver):
        self._old = old

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[Sequence[MajorBlock]]:
        return text_docs.single_pre_formatted_line_object(self._old.resolve(environment))
