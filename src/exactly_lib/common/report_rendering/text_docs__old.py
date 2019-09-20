from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.util.simple_textstruct.rendering import blocks
from exactly_lib.util.simple_textstruct.rendering.components import LineObjectRenderer
from exactly_lib.util.simple_textstruct.structure import LineObject, PreFormattedStringLineObject


def of_err_msg_resolver(resolver: ErrorMessageResolver) -> TextRenderer:
    return blocks.MajorBlocksOfSingleLineObject(
        _ErrorMessageResolverLineObject(resolver)
    )


class _ErrorMessageResolverLineObject(LineObjectRenderer):
    def __init__(self, resolver: ErrorMessageResolver):
        self._resolver = resolver

    def render(self) -> LineObject:
        return PreFormattedStringLineObject(self._resolver.resolve(),
                                            False)
