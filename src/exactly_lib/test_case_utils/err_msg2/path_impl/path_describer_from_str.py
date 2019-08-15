from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForResolver, PathDescriberForValue, \
    PathDescriberForPrimitive
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import LineElement


class PathDescriberForResolverFromStr(PathDescriberForResolver):
    def __init__(self,
                 resolver: Renderer[str],
                 ):
        self._resolver = resolver

    @property
    def resolver(self) -> Renderer[LineElement]:
        return _PathRendererFromStr(self._resolver)


class PathDescriberForValueFromStr(PathDescriberForValue):
    def __init__(self,
                 resolver: PathDescriberForResolver,
                 value: Renderer[str],
                 ):
        self._resolver = resolver
        self._value = value

    @property
    def resolver(self) -> Renderer[LineElement]:
        return self._resolver.resolver

    @property
    def value(self) -> Renderer[LineElement]:
        return _PathRendererFromStr(self._value)


class PathDescriberForPrimitiveFromStr(PathDescriberForPrimitive):
    def __init__(self,
                 value: PathDescriberForValue,
                 primitive: Renderer[str],
                 ):
        self._value = value
        self._primitive = primitive

    @property
    def resolver(self) -> Renderer[LineElement]:
        return self._value.resolver

    @property
    def value(self) -> Renderer[LineElement]:
        return self._value.value

    @property
    def primitive(self) -> Renderer[LineElement]:
        return _PathRendererFromStr(self._primitive)


class _PathRendererFromStr(Renderer[LineElement]):
    def __init__(self,
                 str_renderer: Renderer[str]
                 ):
        self._str_renderer = str_renderer

    def render(self) -> LineElement:
        return LineElement(
            structure.StringLineObject(
                self._str_renderer.render()
            )
        )
