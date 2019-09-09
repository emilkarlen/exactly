from typing import Sequence, Optional, Any

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case_utils.err_msg import path_description as old_path_description
from exactly_lib.test_case_utils.err_msg2.env_dep_text import RendererResolver, SequenceRendererResolver
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering import \
    renderer_combinators as rend_comb, \
    component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import LineElement, MinorBlock, MajorBlock


class PathValueLinesResolver(SequenceRendererResolver[LineElement]):
    def __init__(self,
                 path_resolver: FileRefResolver,
                 header_line: Optional[Any] = None,
                 ):
        self._header_line = header_line
        self._path_resolver = path_resolver

    def resolve_sequence(self, environment: ErrorMessageResolvingEnvironment) -> SequenceRenderer[LineElement]:
        return PathValueLinesRenderer(environment,
                                      self._path_resolver,
                                      self._header_line)


class PathValueMinorBlockResolver(RendererResolver[MinorBlock]):
    def __init__(self,
                 path_resolver: FileRefResolver,
                 header_line: Optional[Any] = None,
                 ):
        self._path_resolver = path_resolver
        self._header_line = header_line

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[MinorBlock]:
        return comp_rend.MinorBlockR(
            PathValueLinesRenderer(environment,
                                   self._path_resolver,
                                   self._header_line)
        )


class PathValueMajorBlockResolver(RendererResolver[MajorBlock]):
    def __init__(self,
                 path_resolver: FileRefResolver,
                 header_line: Optional[Any] = None,
                 ):
        self._path_resolver = path_resolver
        self._header_line = header_line

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> Renderer[MajorBlock]:
        return comp_rend.MajorBlockR(
            rend_comb.SingletonSequenceR(
                PathValueMinorBlockResolver(self._path_resolver,
                                            self._header_line).resolve(environment)
            )
        )


class PathValueLinesRenderer(SequenceRenderer[LineElement]):
    def __init__(self,
                 environment: ErrorMessageResolvingEnvironment,
                 path_resolver: FileRefResolver,
                 header_line: Optional[Any] = None,
                 ):
        self._environment = environment
        self._path_resolver = path_resolver
        self._header_line = header_line

    def render_sequence(self) -> Sequence[LineElement]:
        lines_constructor = old_path_description.PathValuePartConstructor(self._path_resolver)
        lines = lines_constructor.lines(self._environment)
        if self._header_line is not None:
            lines.insert(0, str(self._header_line))

        return [
            LineElement(text_struct.StringLineObject(line))
            for line in lines
        ]


def path_value_minor_block_renderer(environment: ErrorMessageResolvingEnvironment,
                                    path_resolver: FileRefResolver,
                                    header_line: Optional[Any] = None) -> Renderer[MinorBlock]:
    return PathValueMinorBlockResolver(path_resolver, header_line).resolve(environment)


def path_value_major_block_renderer(environment: ErrorMessageResolvingEnvironment,
                                    path_resolver: FileRefResolver,
                                    header_line: Optional[Any] = None) -> Renderer[MajorBlock]:
    return PathValueMajorBlockResolver(path_resolver, header_line).resolve(environment)
