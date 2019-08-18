from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForResolver, PathDescriberForValue, \
    PathDescriberForPrimitive
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class PathDescriberForResolverFromStr(PathDescriberForResolver):
    def __init__(self,
                 resolver: Renderer[str],
                 ):
        self._resolver = resolver

    @property
    def resolver(self) -> Renderer[str]:
        return self._resolver


class PathDescriberForValueFromStr(PathDescriberForValue):
    def __init__(self,
                 resolver: PathDescriberForResolver,
                 value: Renderer[str],
                 ):
        self._resolver = resolver
        self._value = value

    @property
    def resolver(self) -> Renderer[str]:
        return self._resolver.resolver

    @property
    def value(self) -> Renderer[str]:
        return self._value


class PathDescriberForPrimitiveFromStr(PathDescriberForPrimitive):
    def __init__(self,
                 value: PathDescriberForValue,
                 primitive: Renderer[str],
                 ):
        self._value = value
        self._primitive = primitive

    @property
    def resolver(self) -> Renderer[str]:
        return self._value.resolver

    @property
    def value(self) -> Renderer[str]:
        return self._value.value

    @property
    def primitive(self) -> Renderer[str]:
        return self._primitive
