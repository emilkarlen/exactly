from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class PathResolverShouldNotBeUsed(Renderer[str]):
    def __init__(self, path_resolver: FileRefResolver):
        self._path_resolver = path_resolver

    def render(self) -> str:
        raise NotImplementedError('should not be used')
